from rest_framework import serializers

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
    User,
    WasteBucketChoices,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]  # noqa: RUF012


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = "__all__"


class CompartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compartment
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
        fields = ["id", "name", "location"]  # noqa: RUF012


class CaptureSerializer(serializers.ModelSerializer):
    uploaded_by_detail = UserSerializer(source="uploaded_by", read_only=True)

    class Meta:
        model = Capture
        fields = "__all__"
        read_only_fields = ["device", "source", "uploaded_by", "status", "received_at"]  # noqa: RUF012


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = "__all__"
        read_only_fields = ["uploaded_by", "status", "received_at"]  # noqa: RUF012


class LabelSerializer(serializers.ModelSerializer):
    labeler = serializers.HiddenField(default=serializers.CurrentUserDefault())
    labeler_detail = UserSerializer(source="labeler", read_only=True)

    class Meta:
        model = Label
        fields = "__all__"


class OverproductionLogSerializer(serializers.ModelSerializer):
    entered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    entered_by_detail = UserSerializer(source="entered_by", read_only=True)

    class Meta:
        model = OverproductionLog
        fields = "__all__"


class SaveHumanLabelInputSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.filter(active=True))
    waste_bucket = serializers.ChoiceField(choices=WasteBucketChoices.choices)
