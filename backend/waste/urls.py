from rest_framework.routers import DefaultRouter

from .views import (
    CaptureViewSet,
    CompartmentViewSet,
    DeviceViewSet,
    DishViewSet,
    LabelViewSet,
    MenuDayViewSet,
    MenuItemViewSet,
    OverproductionLogViewSet,
    PredictionViewSet,
)

router = DefaultRouter()
router.register("dishes", DishViewSet)
router.register("compartment", CompartmentViewSet)
router.register("menu-days", MenuDayViewSet)
router.register("menu-items", MenuItemViewSet)
router.register("devices", DeviceViewSet)
router.register("captures", CaptureViewSet)
router.register("predictions", PredictionViewSet)
router.register("labels", LabelViewSet)
router.register("overproduction-logs", OverproductionLogViewSet)

urlpatterns = router.urls
