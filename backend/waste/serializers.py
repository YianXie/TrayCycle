from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from .models import (
    Capture,
    Device,
    Dish,
    Label,
    MenuDay,
    OverproductionLog,
    Prediction,
    Station,
    User,
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
    dishes = PrimaryKeyRelatedField(queryset=Dish.objects.all(), many=True)
    dishes_detail = DishSerializer(source="dishes", many=True, read_only=True)

    class Meta:
        model = MenuDay
        fields = ["id", "date", "dishes", "dishes_detail"]  # noqa: RUF012


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
    capture = PrimaryKeyRelatedField(queryset=Capture.objects.all())
    capture_detail = CaptureSerializer(source="capture", read_only=True)
    dish = PrimaryKeyRelatedField(queryset=Dish.objects.all())
    dish_detail = DishSerializer(source="dish", read_only=True)
    labeler = UserSerializer(read_only=True)

    class Meta:
        model = Label
        fields = [  # noqa: RUF012
            "id",
            "capture",
            "capture_detail",
            "dish",
            "dish_detail",
            "waste_bucket",
            "labeler",
        ]

    def validate(self, attrs: dict) -> dict:
        """Reject a second label by the same user for the current capture and dish.

        Args:
            attrs (dict): Validated fields value

        Raises:
            serializers.ValidationError: If the user has already labeled this capture and dish.

        Returns:
            dict: The unchanged attrs.
        """
        capture = attrs.get("capture", getattr(self.instance, "capture", None))
        dish = attrs.get("dish", getattr(self.instance, "dish", None))
        duplicates = Label.objects.filter(
            capture=capture, dish=dish, labeler=self.context["request"].user
        )
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                "You already labeled this dish on this capture."
            )
        return attrs


class OverproductionLogSerializer(ModelSerializer):
    dish = PrimaryKeyRelatedField(queryset=Dish.objects.all())
    dish_detail = DishSerializer(source="dish", read_only=True)
    entered_by = UserSerializer(read_only=True)

    class Meta:
        model = OverproductionLog
        fields = [  # noqa: RUF012
            "id",
            "date",
            "dish",
            "dish_detail",
            "overproduced_kg",
            "entered_by",
        ]


class UpdateMenuDayInputSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(), allow_null=False
    )


class UpdateMenuDaySerializer(serializers.Serializer):
    items = UpdateMenuDayInputSerializer(many=True, allow_empty=False)
