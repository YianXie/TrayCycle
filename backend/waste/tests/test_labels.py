from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class LabelAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Label API."""

    def test_list_requires_auth(self) -> None:
        """Test anonymous requests are rejected."""
        res = self.client.get(reverse("label-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_forbidden(self) -> None:
        """Test logged-in non-staff users get 403 because of the IsAdminUser default."""
        self.login_student()
        res = self.client.get(reverse("label-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
