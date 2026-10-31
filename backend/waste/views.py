import secrets
from collections import defaultdict

from django.db import transaction
from django.db.models import (
    Aggregate,
    Avg,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .authentication import DeviceTokenAuthentication
from .constants import (
    CAPTURE_CLAIM_BATCH_SIZE,
    CAPTURE_FAILURE_REASON_MAX_LENGTH,
    CAPTURE_MAX_ATTEMPTS,
    CAPTURE_TIMEOUT_MINUTES,
    SourceChoices,
    StatusChoices,
)
from .exceptions import ConflictException
from .filters import CaptureFilter, PredictionStatsFilter
from .models import (
    Capture,
    Device,
    Dish,
    Label,
    MenuDay,
    OverproductionLog,
    Prediction,
    Station,
)
from .pagination import CaptureResultsPagination
from .permissions import IsDeviceOrAdmin, IsWorkerOrAdmin
from .serializers import (
    CaptureSerializer,
    DeviceSerializer,
    DishSerializer,
    LabelSerializer,
    MenuDaySerializer,
    OverproductionLogSerializer,
    PredictionSerializer,
    StationSerializer,
    UpdateMenuDaySerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


class MenuDayViewSet(viewsets.ModelViewSet):
    queryset = MenuDay.objects.all()
    serializer_class = MenuDaySerializer

    lookup_field = "date"

    def get_permissions(self) -> list:
        """Override the default permissions to allow workers to list menu days.

        Returns:
            list: A list of permission instances.
        """
        if self.action in ("list", "retrieve"):
            return [IsWorkerOrAdmin()]
        return [IsAdminUser()]

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Override the default update method to allow updating by date.

        Args:
            request (Request): The incoming request object.

        Raises:
            ValidationError: If the provided date is not in a valid YYYY-MM-DD format.

        Returns:
            Response: A Response object containing the serialized menu day data and HTTP status code.
        """
        try:
            date_obj = parse_date(str(kwargs.get("date", "")))
        except ValueError:
            date_obj = None
        if date_obj is None:
            raise ValidationError({"date": "Use a valid YYYY-MM-DD date."})

        input_serializer = UpdateMenuDaySerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        items = input_serializer.validated_data["items"]  # pyright: ignore[reportInvalidTypeArguments, reportOptionalSubscript, reportIndexIssue]

        with transaction.atomic():
            menu_day, created = MenuDay.objects.get_or_create(date=date_obj)
            menu_day.dishes.set([item["dish"] for item in items])  # pyright: ignore[reportGeneralTypeIssues]

        return Response(
            self.get_serializer(menu_day).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Override the default create method to allow creation of a device with a generated token.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: A Response object containing the serialized device data and HTTP status code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = serializer.save()
        return Response(
            {**serializer.data, "token": device.token},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="rotate-token")
    def rotate_token(self, request: Request, pk: str | None = None) -> Response:
        """Rotate the token for a device instance.

        Args:
            request (Request): The incoming request object.
            pk (str | None, optional): Primary key of the device (injected by the router). Defaults to None.

        Returns:
            Response: A Response object containing the serialized device data with the new token and HTTP status code.
        """
        device = self.get_object()
        device.token = secrets.token_urlsafe()
        device.save(update_fields=["token"])
        return Response(
            {"id": device.id, "token": device.token}, status=status.HTTP_200_OK
        )


class CaptureViewSet(viewsets.ModelViewSet):
    queryset = Capture.objects.select_related(
        "device",
        "uploaded_by",
        "claimed_by",
    ).prefetch_related("predictions__capture")
    serializer_class = CaptureSerializer
    pagination_class = CaptureResultsPagination

    authentication_classes = [  # noqa: RUF012
        DeviceTokenAuthentication,
        *api_settings.DEFAULT_AUTHENTICATION_CLASSES,  # pyright: ignore[reportOptionalIterable]
    ]

    def get_permissions(self) -> list:
        """Override the default permissions to allow devices to create captures and workers to list captures.

        Returns:
            list: A list of permission instances.
        """
        if self.action == "create":
            return [IsDeviceOrAdmin()]
        if self.action in ("claim", "fail"):
            return [IsWorkerOrAdmin()]
        return [IsAdminUser()]

    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        """List captures with optional filtering by start and end dates.

        Args:
            request (Request): The incoming request object containing query parameters for filtering captures.

        Returns:
            Response: A Response object containing the serialized capture data and HTTP status code.
        """
        filterset = CaptureFilter(request.query_params, queryset=self.get_queryset())
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(filterset.qs.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Create a new capture instance.

        Args:
            request (Request): The incoming request object containing the capture data.

        Returns:
            Response: A Response object containing the serialized capture data and HTTP status code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if isinstance(self.request.auth, Device):  # pyright: ignore[reportAttributeAccessIssue]
            serializer.save(
                device=self.request.auth,  # pyright: ignore[reportAttributeAccessIssue]
                uploaded_by=None,
                source=SourceChoices.CAMERA,
            )
        else:
            serializer.save(
                device=None,
                uploaded_by=self.request.user,
                source=SourceChoices.UPLOAD,
            )

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="claim")
    def claim(self, request: Request) -> Response:
        """Claim capture instances for processing. Set any captures that have been processing for longer than the timeout to pending, and then claim up to 3 captures for processing.

        Args:
            request (Request): The incoming request object.
        """
        with transaction.atomic():
            processing_queryset = Capture.objects.select_for_update(
                skip_locked=True
            ).filter(status=StatusChoices.PROCESSING)
            for capture in processing_queryset:
                if capture.claimed_at is None:
                    capture.claimed_at = timezone.localtime()
                    capture.save(update_fields=["claimed_at"])
                elif (timezone.localtime() - capture.claimed_at) > timezone.timedelta(  # pyright: ignore[reportOperatorIssue]
                    minutes=CAPTURE_TIMEOUT_MINUTES
                ):
                    capture.status = StatusChoices.PENDING
                    capture.save(update_fields=["status"])

        response_data = []
        with transaction.atomic():
            pending_queryset = (
                Capture.objects.select_for_update(skip_locked=True)
                .filter(status=StatusChoices.PENDING)
                .order_by("received_at")
            )
            while len(response_data) < CAPTURE_CLAIM_BATCH_SIZE:
                batch = list(
                    pending_queryset[: CAPTURE_CLAIM_BATCH_SIZE - len(response_data)]
                )
                if not batch:
                    break
                for capture in batch:
                    capture.status = StatusChoices.PROCESSING
                    capture.attempts += 1
                    update_fields = ["status", "attempts"]
                    if capture.attempts <= CAPTURE_MAX_ATTEMPTS:
                        capture.claimed_at = timezone.localtime()
                        capture.claimed_by = request.user
                        update_fields.extend(["claimed_at", "claimed_by"])
                        response_data.append(self.get_serializer(capture).data)
                    else:
                        capture.status = StatusChoices.FAILED
                        capture.failure_reason = "Exceeded maximum processing attempts."
                        update_fields.append("failure_reason")
                    capture.save(update_fields=update_fields)
        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request: Request, pk: str | None = None) -> Response:
        """Mark a capture as failed and set the status of the associated capture to "failed".

        Args:
            request (Request): The incoming request object.
            pk (str | None, optional): Primary key of the capture (injected by the router). Defaults to None.

        Raises:
            ConflictException: If the capture is not marked as processing or if it is claimed by another

        Returns:
            Response: A Response object containing the serialized capture data and HTTP status code.
        """
        with transaction.atomic():
            try:
                capture = Capture.objects.select_for_update(skip_locked=True).get(pk=pk)
                if capture.status != StatusChoices.PROCESSING:
                    raise ConflictException(
                        "Capture not marked as processing, cannot mark as failed."
                    )
                if (
                    request.user.is_staff is False
                    and capture.claimed_by != request.user
                ):
                    raise ConflictException(
                        "Capture claimed by another user, cannot mark as failed."
                    )
                capture.status = StatusChoices.FAILED
                failure_reason = str(request.data.get("failure_reason", ""))  # pyright: ignore[reportAttributeAccessIssue]
                capture.failure_reason = failure_reason[
                    :CAPTURE_FAILURE_REASON_MAX_LENGTH
                ]
                capture.save(update_fields=["status", "failure_reason"])
            except Capture.DoesNotExist:
                raise ConflictException(
                    "Capture is locked by another process, cannot mark as failed."
                )
        return Response(self.get_serializer(capture).data, status=status.HTTP_200_OK)


class PredictionViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Prediction.objects.select_related(
        "capture", "dish", "dish__station", "capture__device", "capture__uploaded_by"
    )
    serializer_class = PredictionSerializer

    def get_permissions(self) -> list:
        """Override the default permissions to allow workers to create predictions.

        Returns:
            list: A list of permission instances.
        """
        if self.action == "create":
            return [IsWorkerOrAdmin()]
        return [IsAdminUser()]

    def perform_create(self, serializer: PredictionSerializer) -> None:
        """Override the default perform_create method to ensure that the associated capture is marked as pending or processing before creating a prediction.

        Args:
            serializer (PredictionSerializer): The serializer instance used for creating the Prediction.

        Raises:
            ConflictException: If the associated capture is not marked as pending or processing.
        """
        if serializer.validated_data["capture"].status != StatusChoices.PROCESSING:  # type: ignore
            raise ConflictException(
                "Capture not marked as processing, cannot create prediction."
            )
        with transaction.atomic():
            try:
                capture = Capture.objects.select_for_update(skip_locked=True).get(
                    pk=serializer.validated_data["capture"].pk  # type: ignore
                )
                if capture.status == StatusChoices.PROCESSING:
                    capture.status = StatusChoices.DONE
                    capture.save(update_fields=["status"])
                    serializer.validated_data["capture"] = capture  # type: ignore
                    serializer.save()
            except Capture.DoesNotExist:
                raise ConflictException(
                    "Capture is locked by another process, cannot create prediction."
                )


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

    def perform_create(self, serializer: LabelSerializer) -> None:
        """Override the default perform_create method to set the labeler field to the current user.

        Args:
            serializer (LabelSerializer): The serializer instance used for creating the Label.
        """
        serializer.save(labeler=self.request.user)


class OverproductionLogViewSet(viewsets.ModelViewSet):
    queryset = OverproductionLog.objects.all()
    serializer_class = OverproductionLogSerializer

    def perform_create(self, serializer: OverproductionLogSerializer) -> None:
        """Override the default perform_create method to set the entered_by field to the current user.

        Args:
            serializer (OverProductionLogSerializer): The serializer instance used for creating the OverproductionLog.
        """
        serializer.save(entered_by=self.request.user)


WASTE_KG = ExpressionWrapper(
    F("final_waste_bucket") * F("final_portion") / 100000.0,
    output_field=FloatField(),
)


def final_results() -> QuerySet:
    """Build one row per capture: its latest prediction, overridden by its latest human label if one exists.

    Returns:
        QuerySet: Predictions annotated with final_dish_id, final_waste_bucket, final_portion and final_dish_name.
    """
    latest_prediction = Prediction.objects.filter(capture=OuterRef("capture")).order_by(
        "-created_at", "-id"
    )
    latest_label = Label.objects.filter(capture=OuterRef("capture")).order_by("-id")
    final_dish = Dish.objects.filter(pk=OuterRef("final_dish_id"))
    return (
        Prediction.objects.filter(pk=Subquery(latest_prediction.values("pk")[:1]))
        .annotate(
            final_dish_id=Coalesce(
                Subquery(latest_label.values("dish")[:1]),
                F("dish_id"),
                output_field=IntegerField(),
            ),
            final_waste_bucket=Coalesce(
                Subquery(latest_label.values("waste_bucket")[:1]), F("waste_bucket")
            ),
        )
        .annotate(
            final_portion=Subquery(final_dish.values("portion")[:1]),
            final_dish_name=Subquery(final_dish.values("name")[:1]),
        )
    )


def waste_metrics() -> dict[str, Aggregate]:
    """Build the aggregate shared by the overall share and per-dish rows.

    Returns:
        dict[str, Aggregate]: The aggregated key mapped to its expression.
    """
    return {
        "bowl_count": Count("id"),
        "average_waste_percent": Avg("final_waste_bucket"),
        "total_waste_kg": Sum(WASTE_KG),
        "average_waste_kg": Avg(WASTE_KG),
    }


def clean(row: dict) -> dict:
    """Clean the row to remove any None values and round floats to 3 decimal places.

    Args:
        row (dict): The row to clean.

    Returns:
        dict: The cleaned row.
    """
    return {
        key: 0
        if value is None
        else round(value, 3)
        if isinstance(value, float)
        else value
        for key, value in row.items()
    }


class StatsView(APIView):
    def get(self, request: Request) -> Response:
        """Get the statistics for predictions based on the provided filters, counting each capture once with its latest prediction or, if labeled, its latest human label.

        Args:
            request (Request): The incoming request object containing query parameters for filtering predictions.

        Returns:
            Response: A Response object containing the aggregated statistics, per-dish statistics, and daily trends (overall and per dish) based on the filtered predictions.
        """
        filterset = PredictionStatsFilter(
            request.query_params, queryset=final_results()
        )
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        predictions = filterset.qs

        per_dish = (
            predictions.values("final_dish_id", "final_dish_name")
            .annotate(**waste_metrics())
            .order_by("-total_waste_kg")
        )

        per_dish_waste_bucket_distribution = predictions.values(
            "final_dish_id", "final_waste_bucket"
        )
        waste_bucket_distribution = defaultdict(lambda: defaultdict(int))
        for row in per_dish_waste_bucket_distribution:
            waste_bucket_distribution[row["final_dish_id"]][
                row["final_waste_bucket"]
            ] += 1

        by_date = predictions.annotate(date=TruncDate("capture__captured_at"))
        daily = by_date.values("date").annotate(**waste_metrics()).order_by("date")
        per_dish_daily = (
            by_date.values("final_dish_id", "date")
            .annotate(**waste_metrics())
            .order_by("date")
        )
        dish_trends = defaultdict(list)
        for row in per_dish_daily:
            dish_trends[row.pop("final_dish_id")].append(clean(row))

        return Response(
            {
                **clean(predictions.aggregate(**waste_metrics())),
                "daily": [clean(row) for row in daily],
                "dishes": [
                    {
                        "dish_id": (dish_id := row.pop("final_dish_id")),
                        "dish_name": row.pop("final_dish_name"),
                        **clean(row),
                        "daily": dish_trends[dish_id],
                        "waste_bucket_distribution": waste_bucket_distribution[dish_id],
                    }
                    for row in per_dish
                ],
            },
            status=status.HTTP_200_OK,
        )


class ForecastView(APIView):
    def get(self, request: Request) -> Response:
        """Get a forecast of the waste data.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: A Response object containing the forecast data and HTTP status code.
        """
        return Response("Not implemented yet", status=status.HTTP_501_NOT_IMPLEMENTED)
