from django.urls import reverse
from rest_framework import status

from waste.models import Capture, Dish, Prediction

from .shared import WasteAPITestCase, make_image


class DishAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the Dish API."""

    def test_admin_can_create(self) -> None:
        """Test staff members can create a Dish and the response echoes it back."""
        self.login_admin()
        res = self.client.post(
            reverse("dish-list"),
            {"name": "Fried rice", "portion": 300, "station": self.station.id},  # pyright: ignore[reportAttributeAccessIssue]
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["name"], "Fried rice")  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            res.data["station_detail"],  # pyright: ignore[reportAttributeAccessIssue]
            {
                "id": self.station.id,  # pyright: ignore[reportAttributeAccessIssue]
                "name": self.station.name,
                "is_customizable": self.station.is_customizable,
            },
        )
        self.assertTrue(Dish.objects.filter(name="Fried rice").exists())

    def test_invalid_station_id_rejected(self) -> None:
        """Test that providing an invalid station ID returns a 400 error."""
        self.login_admin()
        res = self.client.post(
            reverse("dish-list"),
            {
                "name": "Veggie stir fry",
                "portion": 250,
                "station": 9999,
            },  # Invalid station ID
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertIn("station", res.data)  # pyright: ignore[reportAttributeAccessIssue]

    def test_delete_dish_with_labels_rejected(self) -> None:
        """Test that deleting a dish with associated labels is rejected."""
        self.login_admin()
        capture = Capture.objects.create(image=make_image())
        self.client.post(
            reverse("label-list"),
            data={
                "capture": capture.pk,
                "dish": self.dish.pk,
                "waste_bucket": 0,
            },
        )
        res = self.client.delete(reverse("dish-detail", args=[self.dish.id]))  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_delete_dish_with_overproduction_logs_rejected(self) -> None:
        """Test that deleting a dish with associated overproduction logs is rejected."""
        self.login_admin()
        self.client.post(
            reverse("overproductionlog-list"),
            {
                "date": "2024-01-01",
                "dish": self.dish.pk,
                "overproduced_kg": 5.0,
            },
        )
        res = self.client.delete(reverse("dish-detail", args=[self.dish.id]))  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_delete_dish_with_predictions_rejected(self) -> None:
        """Test that deleting a dish with associated predictions is rejected."""
        self.login_admin()
        capture = Capture.objects.create(image=make_image())
        Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=0,
            confidence=0.9,
            model_version="v1",
        )
        res = self.client.delete(reverse("dish-detail", args=[self.dish.id]))  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)  # pyright: ignore[reportAttributeAccessIssue]

    def test_duplicate_name_rejected(self) -> None:
        """Test Dish.name is unique, so a duplicate returns 400."""
        self.login_admin()
        res = self.client.post(
            reverse("dish-list"),
            {"name": "Chicken rice", "portion": 400, "station": self.station.id},  # pyright: ignore[reportAttributeAccessIssue]
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertIn("name", res.data)  # pyright: ignore[reportAttributeAccessIssue]
