from django.db.utils import IntegrityError
from django.test import override_settings

from waste.models import Capture, Prediction

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class PredictionAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Prediction API."""

    def test_invalid_confidence_rejected(self) -> None:
        """Test that a prediction with confidence outside [0, 1] is rejected."""
        capture = Capture.objects.create(image=make_image())
        with self.assertRaises(IntegrityError):
            Prediction.objects.create(
                capture=capture,
                dish=self.dish,
                waste_bucket=0,
                confidence=1.5,  # Invalid confidence
                model_version="v1",
            )

    def test_invalid_bucket_choice_rejected(self) -> None:
        """Test that a prediction with an invalid waste_bucket choice is rejected."""
        capture = Capture.objects.create(image=make_image())
        with self.assertRaises(IntegrityError):
            Prediction.objects.create(
                capture=capture,
                dish=self.dish,
                waste_bucket=33,  # Invalid bucket choice
                confidence=0.9,
                model_version="v1",
            )
