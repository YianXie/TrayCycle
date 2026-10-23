from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=False)
router.register("stations", views.StationViewSet)
router.register("dishes", views.DishViewSet)
router.register("menu", views.MenuDayViewSet)
router.register("menu-items", views.MenuItemViewSet)
router.register("devices", views.DeviceViewSet)
router.register("captures", views.CaptureViewSet)
router.register("predictions", views.PredictionViewSet)
router.register("labels", views.LabelViewSet)
router.register("overproduction", views.OverproductionLogViewSet)

urlpatterns = [
    path("stats", views.StatsView.as_view(), name="stats"),
    path("forecast", views.ForecastView.as_view(), name="forecast"),
    path("", include(router.urls)),
]
