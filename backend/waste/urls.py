from rest_framework.routers import DefaultRouter

from .views import (
    CaptureViewSet,
    DeviceViewSet,
    DishViewSet,
    LabelViewSet,
    MenuDayViewSet,
    MenuItemViewSet,
    OverproductionLogViewSet,
    PredictionViewSet,
    StationViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("dishes", DishViewSet)
router.register("stations", StationViewSet)
router.register("menu-days", MenuDayViewSet)
router.register("menu-items", MenuItemViewSet)
router.register("devices", DeviceViewSet)
router.register("captures", CaptureViewSet)
router.register("predictions", PredictionViewSet)
router.register("labels", LabelViewSet)
router.register("overproduction-logs", OverproductionLogViewSet)

urlpatterns = router.urls
