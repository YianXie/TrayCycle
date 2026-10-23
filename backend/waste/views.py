import secrets

from django.db import transaction
from django.db.models import (
    Aggregate,
    Avg,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Sum,
)
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .authentication import DeviceTokenAuthentication
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
from .permissions import IsDeviceOrAdmin
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
    queryset = Capture.objects.select_related("device", "uploaded_by").prefetch_related(
        "predictions__dish__station"
    )
    serializer_class = CaptureSerializer

    authentication_classes = [  # noqa: RUF012
        DeviceTokenAuthentication,
        *api_settings.DEFAULT_AUTHENTICATION_CLASSES,  # type: ignore
    ]

    permission_classes = [IsAdminUser]  # noqa: RUF012

    def get_permissions(self) -> list:
        """Override the default permissions to allow any user to create a capture.

        Returns:
            list: A list of permission instances.
        """
        if self.action == "create":
            return [IsDeviceOrAdmin()]
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
                source=Capture.Sources.CAMERA,
            )
        else:
            serializer.save(
                device=None,
                uploaded_by=self.request.user,
                source=Capture.Sources.UPLOAD,
            )

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer


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
    F("waste_bucket") * F("dish__portion") / 100000.0, output_field=FloatField()
)


def waste_metrics() -> dict[str, Aggregate]:
    """Build the aggregate shared by the overall share and per-dish rows.

    Returns:
        dict[str, Aggregate]: The aggregated key mapped to its expression.
    """
    return {
        "bowl_count": Count("id"),
        "average_waste_percent": Avg("waste_bucket"),
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
        """Get the statistics for predictions based on the provided filters.

        Args:
            request (Request): The incoming request object containing query parameters for filtering predictions.

        Returns:
            Response: A Response object containing the aggregated statistics and per-dish statistics based on the filtered predictions.
        """
        filterset = PredictionStatsFilter(
            request.query_params, queryset=Prediction.objects.all()
        )
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        predictions = filterset.qs
        per_dish = (
            predictions.values("dish_id", dish_name=F("dish__name"))
            .annotate(**waste_metrics())
            .order_by("-total_waste_kg")
        )
        return Response(
            {
                **clean(predictions.aggregate(**waste_metrics())),
                "dishes": [clean(row) for row in per_dish],
            }
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
