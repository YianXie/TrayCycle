from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r"stations", views.StationViewSet)
router.register(r"dishes", views.DishViewSet)
router.register(r"menus", views.MenuDayViewSet)
router.register(r"devices", views.DeviceViewSet)
router.register(r"captures", views.CaptureViewSet)
router.register(r"predictions", views.PredictionViewSet)
router.register(r"labels", views.LabelViewSet)
router.register(r"overproduction", views.OverproductionLogViewSet)

urlpatterns = [
    path(r"health", views.HealthCheckView.as_view(), name="health"),
    path(r"stats", views.StatsView.as_view(), name="stats"),
    path(r"forecast", views.ForecastView.as_view(), name="forecast"),
    path("", include(router.urls)),
]
