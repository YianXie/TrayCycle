from django.db.utils import IntegrityError
from django.test import override_settings

from waste.models import Capture, Prediction
from waste.serializers import PredictionSerializer

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class PredictionAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Prediction API."""

    def test_invalid_confidence_rejected(self) -> None:
        """Test that a prediction with confidence outside [0, 1] is rejected."""
        capture = Capture.objects.create(image=make_image())
        serializer = PredictionSerializer(
            data={
                "capture": capture.pk,
                "dish": self.dish.pk,
                "waste_bucket": 0,
                "confidence": {"dish_name": 1.5, "waste_bucket": 0.5},  # Invalid
                "time_taken": 1.0,
                "model_version": "v1",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("confidence", serializer.errors)

    def test_invalid_bucket_choice_rejected(self) -> None:
        """Test that a prediction with an invalid waste_bucket choice is rejected."""
        capture = Capture.objects.create(image=make_image())
        with self.assertRaises(IntegrityError):
            Prediction.objects.create(
                capture=capture,
                dish=self.dish,
                waste_bucket=33,  # Invalid bucket choice
                confidence={"dish_name": 0.9, "waste_bucket": 0.9},
                time_taken=1.0,
                model_version="v1",
            )
