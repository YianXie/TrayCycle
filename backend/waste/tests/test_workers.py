from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.constants import CAPTURE_MAX_ATTEMPTS, WORKER_GROUP_NAME, StatusChoices
from waste.models import Capture, User

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

    def login_worker(self) -> None:
        """Authenticate the test client as a worker user, skipping token auth."""
        self.client.force_authenticate(user=self.worker)  # pyright: ignore[reportAttributeAccessIssue]

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
            "confidence": 0.9,
            "model_version": "v1.0",
        }
        prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data
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
            "confidence": 0.9,
            "model_version": "v1.0",
        }
        prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data
        )

        # Check that the prediction creation failed with a 409 Conflict
        self.assertEqual(prediction_response.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_worker_get_403_elsewhere(self):
        """Test that a worker user cannot access endpoints they shouldn't."""
        self.login_worker()

        # Attempt to access the capture list endpoint
        capture_list_response = self.client.get(reverse("capture-list"))
        self.assertEqual(capture_list_response.status_code, status.HTTP_403_FORBIDDEN)  # pyright: ignore[reportAttributeAccessIssue]

        # Attempt to access the prediction list endpoint
        prediction_list_response = self.client.get(reverse("prediction-list"))
        self.assertEqual(
            prediction_list_response.status_code,  # pyright: ignore[reportAttributeAccessIssue]
            status.HTTP_403_FORBIDDEN,
        )

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
            "confidence": 0.9,
            "model_version": "v1.0",
        }
        first_prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data
        )

        # Check that the first prediction was created successfully
        self.assertEqual(first_prediction_response.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]

        # Attempt to create a second prediction for the same capture
        second_prediction_response = self.client.post(
            reverse("prediction-list"), prediction_data
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
