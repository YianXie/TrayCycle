from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.models import Capture, Prediction, WasteBucketChoices

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class StatsAPITests(WasteAPITestCase):
    """Check the stats aggregation math against numbers worked out by hand."""

    def test_waste_kg_math(self) -> None:
        """Test two bowls at 50% of a 400 g portion returns 0.2kg each, 0.4 kg total."""
        capture = Capture.objects.create(image=make_image())
        for _ in range(2):
            Prediction.objects.create(
                capture=capture,
                dish=self.dish,
                waste_bucket=WasteBucketChoices.HALF,
                confidence=0.9,
                model_version="test",
            )
        self.login_admin()
        res = self.client.get(reverse("stats"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["bowl_count"], 2)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["total_waste_kg"], 0.4)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["average_waste_kg"], 0.2)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["dishes"][0]["dish_name"], "Chicken rice")  # pyright: ignore[reportAttributeAccessIssue]

    def test_invalid_date_filter(self) -> None:
        """Test a malformed ?start returns 400."""
        self.login_admin()
        res = self.client.get(reverse("stats"), {"start": "not-a-date"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
