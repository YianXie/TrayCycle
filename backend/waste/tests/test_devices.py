from django.urls import reverse
from rest_framework import status

from .shared import WasteAPITestCase


class DeviceAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Device API."""

    def test_admin_can_create(self) -> None:
        """Test staff members can create a Device and the response echoes it back."""
        self.login_admin()
        res = self.client.post(
            reverse("device-list"),
            {"name": "cam-2", "location": "Cafe B"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            res.data["name"],  # pyright: ignore[reportAttributeAccessIssue]
            "cam-2",
        )

    def test_token_generated_on_create(self) -> None:
        """Test a token is generated for a new Device."""
        self.login_admin()
        res = self.client.post(
            reverse("device-list"),
            {"name": "cam-2", "location": "Cafe B"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertIn(
            "token",
            res.data,  # pyright: ignore[reportAttributeAccessIssue]
        )

    def test_token_is_read_only(self) -> None:
        """Test the token field is read-only and cannot be set on create."""
        self.login_admin()
        res = self.client.post(
            reverse("device-list"),
            {"name": "cam-2", "location": "Cafe B", "token": "not-a-real-token"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertNotEqual(
            res.data["token"],  # pyright: ignore[reportAttributeAccessIssue]
            "not-a-real-token",
        )

    def test_token_rotation(self) -> None:
        """Test the token can be rotated via the rotate_token action."""
        self.login_admin()
        res = self.client.post(
            reverse("device-list"),
            {"name": "cam-2", "location": "Cafe B"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        device_id = res.data["id"]  # pyright: ignore[reportAttributeAccessIssue]
        old_token = res.data["token"]  # pyright: ignore[reportAttributeAccessIssue]

        res = self.client.post(reverse("device-rotate-token", args=[device_id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        new_token = res.data["token"]  # pyright: ignore[reportAttributeAccessIssue]
        self.assertNotEqual(old_token, new_token)

    def test_duplicate_name_rejected(self) -> None:
        """Test Device.name is unique, so a duplicate returns 400."""
        self.login_admin()
        res = self.client.post(
            reverse("device-list"),
            {"name": "cam-1", "location": "Cafe B"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertIn("name", res.data)  # pyright: ignore[reportAttributeAccessIssue]
