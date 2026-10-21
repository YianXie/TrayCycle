import secrets

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .authentication import DeviceTokenAuthentication
from .models import (
    Capture,
    Compartment,
    Device,
    Dish,
    Label,
    MenuDay,
    MenuItem,
    OverproductionLog,
    Prediction,
)
from .permissions import IsDeviceOrAdmin
from .serializers import (
    CaptureSerializer,
    CompartmentSerializer,
    DeviceSerializer,
    DishSerializer,
    LabelSerializer,
    MenuDaySerializer,
    MenuItemSerializer,
    OverproductionLogSerializer,
    PredictionSerializer,
    SaveHumanLabelInputSerializer,
)


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


class CompartmentViewSet(viewsets.ModelViewSet):
    queryset = Compartment.objects.all()
    serializer_class = CompartmentSerializer


class MenuDayViewSet(viewsets.ModelViewSet):
    queryset = MenuDay.objects.all()
    serializer_class = MenuDaySerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Override the default create method to allow any user to create a device.

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
    queryset = Capture.objects.all()
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

    def perform_create(self, serializer: CaptureSerializer) -> None:
        """Attach the uploading user to the capture, or leave it null for anonymous uploads.

        Args:
            serializer: The validated capture serializer.
        """
        if isinstance(self.request.auth, Device):  # pyright: ignore[reportAttributeAccessIssue]
            serializer.save(
                device=self.request.auth,  # pyright: ignore[reportAttributeAccessIssue]
                source=Capture.Sources.CAMERA,
                uploaded_by=None,
            )
        else:
            serializer.save(
                device=None,
                source=Capture.Sources.UPLOAD,
                uploaded_by=self.request.user,
            )

    @action(detail=True, methods=["post"], url_path="label")
    def save_human_label(self, request: Request, pk: str | None = None) -> Response:
        """Save a human label for a specific capture.

        Args:
            request (Request): The incoming request object containing the label data.
            pk (str | None, optional): Primary key of the scan (injected by the router). Defaults to None.

        Returns:
            Response: A Response object indicating the success or failure of the label saving operation.
        """
        capture = self.get_object()
        label_serializer = SaveHumanLabelInputSerializer(data=request.data)
        label_serializer.is_valid(raise_exception=True)

        labeler = request.user
        dish = label_serializer.validated_data["dish"]
        waste_bucket = label_serializer.validated_data["waste_bucket"]
        label, created = Label.objects.update_or_create(
            capture=capture,
            dish=dish,
            labeler=labeler,
            defaults={"waste_bucket": waste_bucket},
        )

        return Response(
            LabelSerializer(label).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class OverproductionLogViewSet(viewsets.ModelViewSet):
    queryset = OverproductionLog.objects.all()
    serializer_class = OverproductionLogSerializer
