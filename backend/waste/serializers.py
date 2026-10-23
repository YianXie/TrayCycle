from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

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
    WasteBucketChoices,
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]  # noqa: RUF012


class StationSerializer(ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "is_customizable"]  # noqa: RUF012


class DishSerializer(ModelSerializer):
    station = PrimaryKeyRelatedField(queryset=Station.objects.all())
    station_detail = StationSerializer(source="station", read_only=True)

    class Meta:
        model = Dish
        fields = ["id", "name", "portion", "station", "station_detail"]  # noqa: RUF012


class MenuDaySerializer(ModelSerializer):
    class Meta:
        model = MenuDay
        fields = ["id", "date"]  # noqa: RUF012


class MenuItemSerializer(ModelSerializer):
    menu_day = MenuDaySerializer(read_only=True)
    dish = DishSerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "menu_day", "dish"]  # noqa: RUF012


class DeviceSerializer(ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "location"]  # noqa: RUF012


class PredictionSummarySerializer(ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = [  # noqa: RUF012
            "id",
            "dish",
            "waste_bucket",
            "confidence",
            "model_version",
            "created_at",
        ]


class CaptureSerializer(ModelSerializer):
    device = DeviceSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    predictions = PredictionSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Capture
        fields = [  # noqa: RUF012
            "id",
            "image",
            "captured_at",
            "received_at",
            "device",
            "source",
            "uploaded_by",
            "status",
            "predictions",
        ]
        read_only_fields = ["device", "source", "uploaded_by", "status", "received_at"]  # noqa: RUF012


class PredictionSerializer(ModelSerializer):
    dish = DishSerializer(read_only=True)
    capture = CaptureSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = ["capture", *PredictionSummarySerializer.Meta.fields]  # noqa: RUF012


class LabelSerializer(ModelSerializer):
    labeler = UserSerializer(read_only=True)

    class Meta:
        model = Label
        fields = ["id", "capture", "dish", "waste_bucket", "labeler"]  # noqa: RUF012


class OverproductionLogSerializer(ModelSerializer):
    dish = PrimaryKeyRelatedField(queryset=Dish.objects.all())
    dish_detail = DishSerializer(source="dish", read_only=True)
    entered_by = PrimaryKeyRelatedField(queryset=User.objects.all())
    entered_by_detail = UserSerializer(source="entered_by", read_only=True)

    class Meta:
        model = OverproductionLog
        fields = [  # noqa: RUF012
            "id",
            "dish",
            "dish_detail",
            "overproduced_kg",
            "entered_by",
            "entered_by_detail",
        ]
        read_only_fields = ["entered_by"]  # noqa: RUF012


class SaveHumanLabelInputSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all())
    waste_bucket = serializers.ChoiceField(choices=WasteBucketChoices.choices)


class UpdateMenuDayInputSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(), allow_null=False
    )
    station = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        allow_null=False,
    )


class UpdateMenuDaySerializer(serializers.Serializer):
    items = UpdateMenuDayInputSerializer(many=True, allow_empty=False)
