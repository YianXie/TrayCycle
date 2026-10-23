import django_filters

from .models import Capture, Dish, Prediction, Station


class CaptureFilter(django_filters.FilterSet):
    """Filters for /api/captures: ?start, ?end, ?dish, ?max_confidence."""

    start = django_filters.DateFilter(
        field_name="captured_at",
        lookup_expr="date__gte",
    )
    end = django_filters.DateFilter(
        field_name="captured_at",
        lookup_expr="date__lte",
    )
    dish = django_filters.ModelChoiceFilter(
        field_name="predictions__dish", queryset=Dish.objects.all()
    )
    max_confidence = django_filters.NumberFilter(
        field_name="predictions__confidence", lookup_expr="lte"
    )

    class Meta:
        model = Capture
        fields: list[str] = []  # noqa: RUF012


class PredictionStatsFilter(django_filters.FilterSet):
    """Filters for /api/stats: ?start, ?end, ?dish, ?station."""

    start = django_filters.DateFilter(
        field_name="capture__captured_at",
        lookup_expr="date__gte",
    )
    end = django_filters.DateFilter(
        field_name="capture__captured_at",
        lookup_expr="date__lte",
    )
    station = django_filters.ModelChoiceFilter(
        field_name="dish__station", queryset=Station.objects.all()
    )
    dish = django_filters.ModelChoiceFilter(
        field_name="dish",
        queryset=Dish.objects.all(),
    )

    class Meta:
        model = Prediction
        fields: list[str] = []  # noqa: RUF012
