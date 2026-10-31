import django_filters
from django.db.models import QuerySet

from .constants import StatusChoices
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
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=StatusChoices.choices,
    )

    class Meta:
        model = Capture
        fields: list[str] = []  # noqa: RUF012


class PredictionStatsFilter(django_filters.FilterSet):
    """Filters for /api/stats: ?start, ?end, ?dish, ?station.

    ?dish and ?station match the final dish (the label's dish when one exists), so the queryset must carry the final_dish_id annotation.
    """

    start = django_filters.DateFilter(
        field_name="capture__captured_at",
        lookup_expr="date__gte",
    )
    end = django_filters.DateFilter(
        field_name="capture__captured_at",
        lookup_expr="date__lte",
    )
    station = django_filters.ModelChoiceFilter(
        queryset=Station.objects.all(), method="filter_station"
    )
    dish = django_filters.ModelChoiceFilter(
        queryset=Dish.objects.all(), method="filter_dish"
    )

    class Meta:
        model = Prediction
        fields: list[str] = []  # noqa: RUF012

    def filter_station(
        self, queryset: QuerySet, name: str, value: Station | None
    ) -> QuerySet:
        """Keep rows whose final dish belongs to the given station."""
        if value is None:
            return queryset
        return queryset.filter(
            final_dish_id__in=Dish.objects.filter(station=value).values("pk")
        )

    def filter_dish(
        self, queryset: QuerySet, name: str, value: Dish | None
    ) -> QuerySet:
        """Keep rows whose final dish is the given dish."""
        if value is None:
            return queryset
        return queryset.filter(final_dish_id=value.pk)
