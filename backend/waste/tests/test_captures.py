from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.constants import SourceChoices
from waste.models import Capture, Label, Prediction

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class CaptureAPITests(WasteAPITestCase):
    """CRUD, permission, device-token upload, admin upload, and label action tests for the Capture API."""

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
            confidence={"dish_name": 0.9, "waste_bucket": 0.9},
            time_taken=1.0,
            model_version="v1",
        )
        Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=50,
            confidence={"dish_name": 0.8, "waste_bucket": 0.8},
            time_taken=1.0,
            model_version="v1",
        )
        # Filter captures by the dish of the predictions
        res = self.client.get(
            reverse("capture-list"),
            query_params={"max_confidence": 0.9},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["count"], 1)  # pyright: ignore[reportAttributeAccessIssue] # Only one distinct capture should be returned

    def make_prediction(self, capture: Capture, confidence: float) -> Prediction:
        """Create a prediction for the given capture with the given confidence.

        Args:
            capture (Capture): the capture the prediction belongs to.
            confidence (float): the model confidence of the prediction.

        Returns:
            Prediction: the created prediction.
        """
        return Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=25,
            confidence={"dish_name": confidence, "waste_bucket": confidence},
            time_taken=1.0,
            model_version="v1",
        )

    def needs_review_ids(self) -> set[int]:
        """Return the ids of the captures returned by ?needs_review=true."""
        res = self.client.get(
            reverse("capture-list"),
            query_params={"needs_review": "true"},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        return {row["id"] for row in res.data["results"]}  # pyright: ignore[reportAttributeAccessIssue]

    def test_needs_review_uses_latest_prediction(self) -> None:
        """Test that only the latest prediction's confidence decides whether a capture needs review."""
        self.login_admin()

        # Old low-confidence prediction superseded by a confident one
        recovered = Capture.objects.create(image=make_image())
        self.make_prediction(recovered, 0.4)
        self.make_prediction(recovered, 0.95)

        # Old confident prediction superseded by a low-confidence one
        regressed = Capture.objects.create(image=make_image())
        self.make_prediction(regressed, 0.95)
        self.make_prediction(regressed, 0.4)

        self.assertEqual(self.needs_review_ids(), {regressed.pk})

    def test_needs_review_excludes_labeled_captures(self) -> None:
        """Test that a low-confidence capture that already has a label does not need review."""
        self.login_admin()

        labeled = Capture.objects.create(image=make_image())
        self.make_prediction(labeled, 0.4)
        Label.objects.create(
            capture=labeled, dish=self.dish, waste_bucket=50, labeler=self.admin
        )

        unlabeled = Capture.objects.create(image=make_image())
        self.make_prediction(unlabeled, 0.4)

        self.assertEqual(self.needs_review_ids(), {unlabeled.pk})

    def test_needs_review_excludes_captures_without_predictions(self) -> None:
        """Test that a capture with no predictions yet is not flagged for review."""
        self.login_admin()

        Capture.objects.create(image=make_image())

        self.assertEqual(self.needs_review_ids(), set())
