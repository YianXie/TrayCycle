from django.urls import reverse
from rest_framework import status

from waste.models import Capture

from .shared import make_image


def test_delete_labeler_with_labels_rejected(self) -> None:
    """Test that deleting a user with associated labels is rejected."""
    self.login_admin()
    capture = Capture.objects.create(image=make_image())
    self.client.post(
        reverse("label-list"),
        data={
            "capture": capture.pk,
            "dish": self.dish.pk,
            "waste_bucket": 0,
        },
    )
    res = self.client.delete(reverse("user-detail", args=[self.student.id]))  # pyright: ignore[reportAttributeAccessIssue]
    self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)


def test_delete_user_with_overproduction_logs_rejected(self) -> None:
    """Test that deleting a user with associated overproduction logs is rejected."""
    self.login_admin()
    self.client.post(
        reverse("overproductionlog-list"),
        {
            "date": "2024-01-01",
            "dish": self.dish.pk,
            "overproduced_kg": 5.0,
        },
    )
    res = self.client.delete(reverse("user-detail", args=[self.student.id]))  # pyright: ignore[reportAttributeAccessIssue]
    self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
