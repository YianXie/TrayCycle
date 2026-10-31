import django_filters
from django.db.models import OuterRef, QuerySet, Subquery

from .constants import CAPTURE_REVIEW_THRESHOLD, StatusChoices
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
    needs_review = django_filters.BooleanFilter(
        method="filter_needs_review",
    )

    class Meta:
        model = Capture
        fields: list[str] = []  # noqa: RUF012

    def filter_needs_review(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        """Keep rows whose latest prediction is below the threshold and has no label."""
        if not value:
            return queryset
        latest_prediction = Prediction.objects.filter(capture=OuterRef("pk")).order_by(
            "-created_at", "-id"
        )
        return (
            queryset.annotate(
                latest_confidence=Subquery(latest_prediction.values("confidence")[:1])
            )
            .filter(
                latest_confidence__lt=CAPTURE_REVIEW_THRESHOLD,
                labels__isnull=True,
            )
            .distinct()
        )


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
