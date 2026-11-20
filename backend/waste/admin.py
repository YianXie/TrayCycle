from django.contrib import admin, messages
from django.db import DatabaseError
from django.db.models import QuerySet
from django.http import HttpRequest

from .constants import StatusChoices
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
    list_filter = ("device", "uploaded_by", "source", "status")
    actions = ("mark_as_pending",)

    @admin.action(description="Mark selected captures as pending")
    def mark_as_pending(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Admin action to mark selected captures as pending, ignoring those that are already done.

        Args:
            request: The current admin request.
            queryset: The entries the admin selected.
        """
        try:
            updated: int = queryset.update(
                claimed_at=None,
                claimed_by=None,
                attempts=0,
                status=StatusChoices.PENDING,
                failure_reason=None,
            )
        except DatabaseError as e:
            self.message_user(
                request,
                f"An error occurred while updating captures: {e}",
                level=messages.ERROR,
            )
            return
        self.message_user(
            request,
            f"Successfully marked {updated} capture(s) as pending.",
            level=messages.SUCCESS,
        )


class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ("id", "capture", "dish", "waste_bucket", "created_at")
    list_filter = ("dish", "waste_bucket", "created_at")


class LabelModelAdmin(admin.ModelAdmin):
    list_display = ("id", "capture", "dish", "waste_bucket", "labeler")
    list_filter = ("dish", "waste_bucket", "labeler")


class OverproductionLogModelAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "dish", "overproduced_kg", "entered_by")
    list_filter = ("date", "dish", "entered_by")


admin.site.register(Dish, DishModelAdmin)
admin.site.register(Station, StationModelAdmin)
admin.site.register(MenuDay, MenuDayModelAdmin)
admin.site.register(Device, DeviceModelAdmin)
admin.site.register(Capture, CaptureModelAdmin)
admin.site.register(Prediction, PredictionModelAdmin)
admin.site.register(Label, LabelModelAdmin)
admin.site.register(OverproductionLog, OverproductionLogModelAdmin)
