from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from waste.constants import CAPTURE_MAX_ATTEMPTS, WORKER_GROUP_NAME, StatusChoices
from waste.models import Capture, Prediction, User

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class WorkerTest(WasteAPITestCase):
    """Pending -> processing -> (done | failed) tests for the worker process."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up a few shared objects for all tests in this class."""
        super().setUpTestData()
        cls.worker = User.objects.create_user("worker", password="pw")
        cls.worker.groups.add(Group.objects.get(name=WORKER_GROUP_NAME))
        cls.other_worker = User.objects.create_user("other-worker", password="pw")
        cls.other_worker.groups.add(Group.objects.get(name=WORKER_GROUP_NAME))

    def login_worker(self) -> None:
        """Authenticate the test client as a worker user, skipping token auth."""
        self.client.force_authenticate(user=self.worker)  # pyright: ignore[reportAttributeAccessIssue]

    def login_other_worker(self) -> None:
        """Authenticate the test client as a second worker user, skipping token auth."""
        self.client.force_authenticate(user=self.other_worker)  # pyright: ignore[reportAttributeAccessIssue]

    def make_claimed_capture(self) -> Capture:
        """Create a capture that is processing and claimed by the first worker.

        Returns:
            Capture: the claimed capture.
        """
        return Capture.objects.create(
            image=make_image(),
            status=StatusChoices.PROCESSING,
            claimed_by=self.worker,
            claimed_at=timezone.now(),
            attempts=1,
        )

    def prediction_data(self, capture: Capture) -> dict:
        """Build a valid prediction payload for the given capture.

        Args:
            capture (Capture): the capture the prediction is for.

        Returns:
            dict: the request payload.
        """
        return {
            "capture": capture.pk,
            "dish": self.dish.pk,
            "waste_bucket": 25,
            "confidence": {"dish_name": 0.9, "waste_bucket": 0.9},
            "time_taken": 1.0,
            "model_version": "v1.0",
        }

    def test_prediction_makes_capture_done(self):
        """Test that a prediction marks the capture as done."""
        self.login_admin()

        # Create a capture with status "processing"
        capture = Capture.objects.create(
            image=make_image(),
        )

        # Claim the capture for processing
        self.login_worker()
        claim_response = self.client.post(reverse("capture-claim"))

        # Check that the capture is now marked as processing
        self.assertEqual(claim_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(claim_response.data[0]["status"], StatusChoices.PROCESSING)  # pyright: ignore[reportAttributeAccessIssue]

        # Create a prediction for the capture
        prediction_data = {
            "capture": capture.pk,
            "dish": self.dish.pk,
            "waste_bucket": 25,
            "confidence": {"dish_name": 0.9, "waste_bucket": 0.9},
            "time_taken": 1.0,
            "model_version": "v1.0",
        }
        prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data, format="json"
        )

        # Check that the prediction was created successfully and the capture is now marked as done
        self.assertEqual(prediction_response.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            prediction_response.data["capture_detail"]["status"],  # pyright: ignore[reportAttributeAccessIssue]
            StatusChoices.DONE,
        )

    def test_capture_fail_marks_capture_failed(self):
        """Test that marking a capture as failed updates its status."""
        self.login_admin()

        # Create a capture with status "processing"
        capture = Capture.objects.create(
            image=make_image(),
        )

        # Claim the capture for processing
        self.login_worker()
        claim_response = self.client.post(reverse("capture-claim"))

        # Check that the capture is now marked as processing
        self.assertEqual(claim_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(claim_response.data[0]["status"], StatusChoices.PROCESSING)  # pyright: ignore[reportAttributeAccessIssue]

        # Mark the capture as failed
        fail_response = self.client.post(
            reverse("capture-fail", args=[capture.pk]),
            {"failure_reason": "Test failure reason"},
        )

        # Check that the capture is now marked as failed
        self.assertEqual(fail_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(fail_response.data["status"], StatusChoices.FAILED)  # pyright: ignore[reportAttributeAccessIssue]

    def test_prediction_on_non_processing_capture_fails(self):
        """Test that creating a prediction on a non-processing capture fails."""
        self.login_admin()

        # Create a capture with status "pending"
        capture = Capture.objects.create(
            image=make_image(),
        )

        # Attempt to create a prediction for the capture
        self.login_worker()
        prediction_data = {
            "capture": capture.pk,
            "dish": self.dish.pk,
            "waste_bucket": 25,
            "confidence": {"dish_name": 0.9, "waste_bucket": 0.9},
            "time_taken": 1.0,
            "model_version": "v1.0",
        }
        prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data, format="json"
        )

        # Check that the prediction creation failed with a 409 Conflict
        self.assertEqual(prediction_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_fail_on_non_processing_capture_returns_409(self):
        """Test that marking a non-processing capture as failed returns a 409 Conflict."""
        self.login_admin()

        # Create a capture with status "pending"
        capture = Capture.objects.create(
            image=make_image(),
        )

        # Attempt to mark the capture as failed
        self.login_worker()
        fail_response = self.client.post(
            reverse("capture-fail", args=[capture.pk]),
            {"failure_reason": "Test failure reason"},
        )

        # Check that the response is 409 Conflict
        self.assertEqual(fail_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_second_prediction_for_the_same_capture_returns_409(self):
        """Test that creating a second prediction for the same capture returns a 409 Conflict."""
        self.login_admin()

        # Create a capture with status "processing"
        capture = Capture.objects.create(
            image=make_image(),
        )

        # Claim the capture for processing
        self.login_worker()
        claim_response = self.client.post(reverse("capture-claim"))

        # Check that the capture is now marked as processing
        self.assertEqual(claim_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(claim_response.data[0]["status"], StatusChoices.PROCESSING)  # pyright: ignore[reportAttributeAccessIssue]

        # Create the first prediction for the capture
        prediction_data = {
            "capture": capture.pk,
            "dish": self.dish.pk,
            "waste_bucket": 25,
            "confidence": {"dish_name": 0.9, "waste_bucket": 0.9},
            "time_taken": 1.0,
            "model_version": "v1.0",
        }
        first_prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data, format="json"
        )

        # Check that the first prediction was created successfully
        self.assertEqual(first_prediction_response.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]

        # Attempt to create a second prediction for the same capture
        second_prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data, format="json"
        )

        # Check that the second prediction creation failed with a 409 Conflict
        self.assertEqual(
            second_prediction_response.status_code,  # pyright: ignore[reportAttributeAccessIssue]
            status.HTTP_409_CONFLICT,
        )

    def test_exceeding_max_attempts_fails(self):
        """Test that exceeding the maximum number of attempts for a capture results in a failed status."""
        self.login_admin()

        # Create a capture with status "processing" and max attempts
        capture = Capture.objects.create(
            image=make_image(),
            attempts=CAPTURE_MAX_ATTEMPTS,  # Set attempts to the maximum allowed
        )

        # Claim the capture for processing
        self.login_worker()
        claim_response = self.client.post(reverse("capture-claim"))

        # Check that the capture is now marked as processing
        self.assertEqual(claim_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(len(claim_response.data), 0)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            Capture.objects.filter(id=capture.pk).first().status,  # pyright: ignore[reportOptionalMemberAccess]
            StatusChoices.FAILED,
        )

    def test_fail_on_missing_capture_returns_404(self):
        """Test that marking a capture that does not exist as failed returns a 404 Not Found."""
        self.login_worker()
        fail_response = self.client.post(
            reverse("capture-fail", args=[999999]),
            {"failure_reason": "Test failure reason"},
        )
        self.assertEqual(fail_response.status_code, status.HTTP_404_NOT_FOUND)  # pyright: ignore[reportAttributeAccessIssue]

    def test_fail_by_another_worker_returns_409(self):
        """Test that a worker cannot mark a capture claimed by another worker as failed."""
        capture = self.make_claimed_capture()

        self.login_other_worker()
        fail_response = self.client.post(
            reverse("capture-fail", args=[capture.pk]),
            {"failure_reason": "Test failure reason"},
        )

        # Check that the response is 409 Conflict and the capture is untouched
        self.assertEqual(fail_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]
        capture.refresh_from_db()
        self.assertEqual(capture.status, StatusChoices.PROCESSING)
        self.assertIsNone(capture.failure_reason)

    def test_admin_can_fail_capture_claimed_by_worker(self):
        """Test that a staff user can mark a capture claimed by a worker as failed."""
        capture = self.make_claimed_capture()

        self.login_admin()
        fail_response = self.client.post(
            reverse("capture-fail", args=[capture.pk]),
            {"failure_reason": "Test failure reason"},
        )

        self.assertEqual(fail_response.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        capture.refresh_from_db()
        self.assertEqual(capture.status, StatusChoices.FAILED)
        self.assertEqual(capture.failure_reason, "Test failure reason")

    def test_prediction_by_another_worker_returns_409(self):
        """Test that a worker cannot create a prediction for a capture claimed by another worker."""
        capture = self.make_claimed_capture()

        self.login_other_worker()
        prediction_response = self.client.post(
            reverse("prediction-list"), self.prediction_data(capture), format="json"
        )

        # Check that the response is 409 Conflict, no prediction was saved and the capture is untouched
        self.assertEqual(prediction_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertFalse(Prediction.objects.filter(capture=capture).exists())
        capture.refresh_from_db()
        self.assertEqual(capture.status, StatusChoices.PROCESSING)

    def test_prediction_after_reclaim_by_another_worker_returns_409(self):
        """Test that a worker whose claim timed out cannot complete a capture another worker has reclaimed."""
        capture = self.make_claimed_capture()

        # The second worker reclaims the capture after the first worker's claim timed out
        capture.claimed_by = self.other_worker
        capture.attempts = 2
        capture.save(update_fields=["claimed_by", "attempts"])

        # The first worker posts its late prediction
        self.login_worker()
        late_response = self.client.post(
            reverse("prediction-list"), self.prediction_data(capture), format="json"
        )
        self.assertEqual(late_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

        # The worker that holds the claim can still complete it
        self.login_other_worker()
        current_response = self.client.post(
            reverse("prediction-list"), self.prediction_data(capture), format="json"
        )
        self.assertEqual(current_response.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(Prediction.objects.filter(capture=capture).count(), 1)

    def test_admin_can_create_prediction_for_capture_claimed_by_worker(self):
        """Test that a staff user can create a prediction for a capture claimed by a worker."""
        capture = self.make_claimed_capture()

        self.login_admin()
        prediction_response = self.client.post(
            reverse("prediction-list"), self.prediction_data(capture), format="json"
        )

        self.assertEqual(prediction_response.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        capture.refresh_from_db()
        self.assertEqual(capture.status, StatusChoices.DONE)
