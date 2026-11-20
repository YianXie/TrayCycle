from django.urls import reverse
from rest_framework import status

from .shared import WasteAPITestCase


class OverproductionLogAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the OverproductionLog API."""

    def test_duplicate_overproduction_logs_rejected(self) -> None:
        """Test that the API rejects a duplicate (date, dish) with a 400 validation error."""
        self.login_admin()
        data = {"dish": self.dish.pk, "overproduced_kg": 5.0}
        # Create the first log
        res = self.client.post(reverse("overproductionlog-list"), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        # Attempt to create a duplicate log for the same date and dish
        res = self.client.post(reverse("overproductionlog-list"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
