import random
import time
from typing import TypedDict

from PIL import Image

from worker.exceptions import ModelException


class PredictionResult(TypedDict):
    """A TypedDict representing the structure of a prediction result."""

    dish: str | None
    waste_bucket: int
    confidence: float
    model_version: str


class Predictor:
    """A class representing a model predictor."""

    MODEL_VERSION = "1.0.0"

    def __init__(self):
        """Initialize the Predictor class."""

    def predict(self, image: Image.Image, dishes: list) -> PredictionResult:
        """Dummy prediction function that simulates a model prediction by sleeping for 2 seconds.

        Args:
            image (Image.Image): the input image for which the prediction is to be made.
            dishes (list): a list of available dishes for prediction.

        Raises:
            ModelException: If there are no dishes available for prediction or if a simulated error occurs.

        Returns:
            PredictionResult: A dictionary containing the prediction results.
        """
        time.sleep(2)

        if not dishes:
            raise ModelException("No dishes available for prediction.")

        if random.random() < 0.1:  # 10% chance of failure
            raise ModelException("Prediction failed due to a simulated error.")

        return {
            "dish": random.choice(dishes),
            "waste_bucket": random.choice((0, 25, 50, 75, 100)),
            "confidence": round(random.random(), 2),
            "model_version": Predictor.MODEL_VERSION,
        }
