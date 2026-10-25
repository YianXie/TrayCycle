from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.constants import SourceChoices
from waste.models import Capture, Prediction

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class CaptureAPITests(WasteAPITestCase):
    """CRUD, permission, device-token upload, admin upload, and label action tests for the Capture API."""

    def test_list_requires_auth(self) -> None:
        """Test anonymous requests are rejected."""
        res = self.client.get(reverse("capture-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # pyright: ignore[reportAttributeAccessIssue]

    def test_non_staff_forbidden(self) -> None:
        """Test logged-in non-staff users get 403 because of the IsAdminUser default."""
        self.login_student()
        res = self.client.get(reverse("capture-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # pyright: ignore[reportAttributeAccessIssue]

    def test_device_upload_sets_camera_source(self) -> None:
        """Test a device token creates a CAMERA capture linked to that device."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Device {self.device.token}")  # pyright: ignore[reportAttributeAccessIssue]
        res = self.client.post(
            reverse("capture-list"),
            {"image": make_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)  # pyright: ignore[reportAttributeAccessIssue]
        capture = Capture.objects.get(pk=res.data["id"])  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(capture.device, self.device)
        self.assertEqual(capture.source, SourceChoices.CAMERA)
        self.assertIsNone(capture.uploaded_by)

    def test_bad_device_token_rejected(self) -> None:
        """Test an unknown device token returns 401."""
        self.client.credentials(HTTP_AUTHORIZATION="Device not-a-real-token")
        res = self.client.post(
            reverse("capture-list"), {"image": make_image()}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # pyright: ignore[reportAttributeAccessIssue]

    def test_device_cannot_list(self) -> None:
        """Test devices may only create, not read captures."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Device {self.device.token}")  # pyright: ignore[reportAttributeAccessIssue]
        res = self.client.get(reverse("capture-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # pyright: ignore[reportAttributeAccessIssue]

    def test_admin_upload_sets_upload_source(self) -> None:
        """Test a staff upload records uploaded_by and the UPLOAD source."""
        self.login_admin()
        res = self.client.post(
            reverse("capture-list"), {"image": make_image()}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)  # pyright: ignore[reportAttributeAccessIssue]
        capture = Capture.objects.get(pk=res.data["id"])  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(capture.uploaded_by, self.admin)
        self.assertEqual(capture.source, SourceChoices.UPLOAD)

    def test_only_distinct_captures_returned(self) -> None:
        """Test that the API returns distinct captures when filtering by a related field."""
        self.login_admin()
        capture = Capture.objects.create(image=make_image())
        # Create two predictions for the same capture
        Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=25,
            confidence=0.9,
            model_version="v1",
        )
        Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=50,
            confidence=0.8,
            model_version="v1",
        )
        # Filter captures by the dish of the predictions
        res = self.client.get(
            reverse("capture-list"),
            query_params={"max_confidence": 0.9},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(len(res.data), 1)  # pyright: ignore[reportAttributeAccessIssue] # Only one distinct capture should be returned
