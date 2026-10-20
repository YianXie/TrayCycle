from rest_framework import serializers

from .models import (
    Capture,
    Device,
    Dish,
    Label,
    MenuDay,
    MenuItem,
    OverproductionLog,
    Prediction,
    Station,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]  # noqa: RUF012


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = "__all__"


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"


class MenuDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuDay
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class CaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capture
        fields = "__all__"


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = "__all__"


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = "__all__"


class OverproductionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverproductionLog
        fields = "__all__"
