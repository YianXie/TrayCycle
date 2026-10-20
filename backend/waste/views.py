from rest_framework import viewsets

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


class CaptureViewSet(viewsets.ModelViewSet):
    queryset = Capture.objects.all()
    serializer_class = CaptureSerializer


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class OverproductionLogViewSet(viewsets.ModelViewSet):
    queryset = OverproductionLog.objects.all()
    serializer_class = OverproductionLogSerializer
