from django.contrib import admin

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


class StationModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_customizable")
    list_filter = ("is_customizable",)


class DishModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "portion", "station")
    list_filter = ("station",)


class MenuDayModelAdmin(admin.ModelAdmin):
    list_display = ("id", "date")
    list_filter = ("date",)


class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location")
    list_filter = ("name", "location")


class CaptureModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "captured_at",
        "received_at",
        "device",
        "uploaded_by",
        "source",
        "status",
    )
    list_filters = ("device", "uploaded_by", "source", "status")


class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ("id", "capture", "dish", "waste_bucket", "created_at")
    list_filter = ("dish", "waste_bucket", "created_at")


class LabelModelAdmin(admin.ModelAdmin):
    list_display = ("id", "capture", "dish", "waste_bucket", "labeler")
    list_filter = ("dish", "waste_bucket", "labeler")


class OverproductionLogModelAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "dish", "overproduced_kg", "entered_by")
    list_filter = ("date", "dish", "entered_by")


admin.site.register(User, admin.ModelAdmin)
admin.site.register(Dish, DishModelAdmin)
admin.site.register(Station, StationModelAdmin)
admin.site.register(MenuDay, MenuDayModelAdmin)
admin.site.register(Device, DeviceModelAdmin)
admin.site.register(Capture, CaptureModelAdmin)
admin.site.register(Prediction, PredictionModelAdmin)
admin.site.register(Label, LabelModelAdmin)
admin.site.register(OverproductionLog, OverproductionLogModelAdmin)
