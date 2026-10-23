from django.urls import reverse
from rest_framework import status

from waste.models import Station

from .shared import WasteAPITestCase


class StationAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Station API."""

    def test_list_requires_auth(self) -> None:
        """Test anonymous requests are rejected."""
        res = self.client.get(reverse("station-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_forbidden(self) -> None:
        """Test logged-in non-staff users get 403 because of the IsAdminUser default."""
        self.login_student()
        res = self.client.get(reverse("station-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create(self) -> None:
        """Test staff members can create a Station and the response echoes it back."""
        self.login_admin()
        res = self.client.post(
            reverse("station-list"),
            {"name": "Western", "is_customizable": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Western")  # pyright: ignore[reportAttributeAccessIssue]
        self.assertTrue(Station.objects.filter(name="Western").exists())

    def test_delete_station_with_dishes_rejected(self) -> None:
        """Test that deleting a station with associated dishes returns a 400 error."""
        self.login_admin()
        res = self.client.delete(reverse("station-detail", args=[self.station.id]))  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Station.objects.filter(id=self.station.id).exists())  # pyright: ignore[reportAttributeAccessIssue]

    def test_duplicate_name_rejected(self) -> None:
        """Test Station.name is unique, so a duplicate returns 400."""
        self.login_admin()
        res = self.client.post(
            reverse("station-list"),
            {"name": "Asian", "is_customizable": False},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)  # pyright: ignore[reportAttributeAccessIssue]
