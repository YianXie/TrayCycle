from decimal import Decimal

import django_filters
from django.db.models import OuterRef, Q, QuerySet, Subquery

from .constants import CAPTURE_REVIEW_THRESHOLD, StatusChoices
from .models import Capture, Dish, Prediction, Station

CONFIDENCE_KEYS = ("dish_name", "waste_bucket")


def confidence_below(
    threshold: float, prefix: str = "", *, inclusive: bool = False
) -> Q:
    """Build a Q matching predictions where any confidence score is below the threshold.

    Args:
        threshold (float): The confidence threshold.
        prefix (str): Lookup path to the prediction, e.g. "predictions__".
        inclusive (bool): Use <= instead of <.

    Returns:
        Q: The combined condition.
    """
    lookup = "lte" if inclusive else "lt"
    q = Q()
    for key in CONFIDENCE_KEYS:
        q |= Q(**{f"{prefix}confidence__{key}__{lookup}": threshold})
    return q


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
    max_confidence = django_filters.NumberFilter(method="filter_max_confidence")
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

    def filter_max_confidence(
        self, queryset: QuerySet, name: str, value: Decimal | None
    ) -> QuerySet:
        """Keep rows with a prediction whose dish or waste bucket confidence is at most the value."""
        if value is None:
            return queryset
        return queryset.filter(
            confidence_below(float(value), "predictions__", inclusive=True)
        ).distinct()

    def filter_needs_review(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        """Keep rows whose latest prediction has any confidence below the threshold and no label."""
        if not value:
            return queryset
        latest_prediction = Prediction.objects.filter(capture=OuterRef("pk")).order_by(
            "-created_at", "-id"
        )
        return (
            queryset.annotate(
                latest_prediction_id=Subquery(latest_prediction.values("pk")[:1])
            )
            .filter(
                latest_prediction_id__in=Prediction.objects.filter(
                    confidence_below(CAPTURE_REVIEW_THRESHOLD)
                ).values("pk"),
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
