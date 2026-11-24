import time
from typing import TypedDict

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from worker.exceptions import ModelException


class PredictionResult(TypedDict):
    """A TypedDict representing the structure of a prediction result."""

    dish: int
    waste_bucket: int
    confidence: dict[str, float]
    time_taken: float
    model_version: str


class Predictor:
    """A class representing a model predictor."""

    MODEL = "openai/clip-vit-base-patch32"

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
        if not dishes:
            raise ModelException("No dishes available for prediction.")

        start_time = time.time()

        model = CLIPModel.from_pretrained(self.MODEL)
        processor = CLIPProcessor.from_pretrained(self.MODEL)
        model.eval()

        dish_name_labels = [dish["name"] for dish in dishes]
        inputs = processor(
            text=[f"A picture of {label}" for label in dish_name_labels],
            images=image,
            return_tensors="pt",  # pyright: ignore[reportCallIssue]
            padding=True,  # pyright: ignore[reportCallIssue]
        )

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = outputs.logits_per_image.softmax(dim=1)[0]
        dish_name_results = sorted(
            zip(dish_name_labels, probabilities.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )

        waste_bucket_labels = [0, 25, 50, 75, 100]
        inputs = processor(
            text=[f"{label}% food remaining" for label in waste_bucket_labels],
            images=image,
            return_tensors="pt",  # pyright: ignore[reportCallIssue]
            padding=True,  # pyright: ignore[reportCallIssue]
        )

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = outputs.logits_per_image.softmax(dim=1)[0]
        waste_bucket_results = sorted(
            zip(waste_bucket_labels, probabilities.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )

        end_time = time.time()

        return {
            "dish": next(
                dish["id"] for dish in dishes if dish["name"] == dish_name_results[0][0]
            ),
            "waste_bucket": waste_bucket_results[0][0],
            "confidence": {
                "dish_name": dish_name_results[0][1],
                "waste_bucket": waste_bucket_results[0][1],
            },
            "time_taken": round(end_time - start_time, 2),
            "model_version": self.MODEL,
        }
