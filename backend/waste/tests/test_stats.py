import datetime

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.models import Capture, Dish, Label, Prediction, WasteBucketChoices

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase, make_image


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class StatsAPITests(WasteAPITestCase):
    """Check the stats aggregation math against numbers worked out by hand."""

    def test_waste_kg_math(self) -> None:
        """Test two bowls at 50% of a 400 g portion returns 0.2kg each, 0.4 kg total."""
        for _ in range(2):
            Prediction.objects.create(
                capture=Capture.objects.create(image=make_image()),
                dish=self.dish,
                waste_bucket=WasteBucketChoices.HALF,
                confidence={"dish_name": 0.9, "waste_bucket": 0.9},
                time_taken=1.0,
                model_version="test",
            )
        self.login_admin()
        res = self.client.get(reverse("stats"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["bowl_count"], 2)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["total_waste_kg"], 0.4)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["average_waste_kg"], 0.2)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["dishes"][0]["dish_name"], "Chicken rice")  # pyright: ignore[reportAttributeAccessIssue]

    def test_daily_trend(self) -> None:
        """Test kg per day is bucketed by local (Asia/Singapore) date, overall and per dish."""
        noodles = Dish.objects.create(name="Noodles", portion=200, station=self.station)
        utc = datetime.UTC
        for captured_at, dish, bucket in [
            (
                datetime.datetime(2022, 1, 1, 4, tzinfo=utc),
                self.dish,
                WasteBucketChoices.HALF,
            ),
            (
                datetime.datetime(2022, 1, 1, 20, tzinfo=utc),
                self.dish,
                WasteBucketChoices.ALL,
            ),
            (
                datetime.datetime(2022, 1, 1, 20, tzinfo=utc),
                noodles,
                WasteBucketChoices.HALF,
            ),
        ]:
            Prediction.objects.create(
                capture=Capture.objects.create(
                    image=make_image(), captured_at=captured_at
                ),
                dish=dish,
                waste_bucket=bucket,
                confidence={"dish_name": 0.9, "waste_bucket": 0.9},
                time_taken=1.0,
                model_version="test",
            )
        self.login_admin()
        res = self.client.get(reverse("stats"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        daily = res.data["daily"]  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            [row["date"] for row in daily],
            [datetime.date(2022, 1, 1), datetime.date(2022, 1, 2)],
        )
        self.assertAlmostEqual(daily[0]["total_waste_kg"], 0.2)
        self.assertAlmostEqual(daily[1]["total_waste_kg"], 0.5)
        self.assertEqual(daily[1]["bowl_count"], 2)

        dishes = {d["dish_name"]: d["daily"] for d in res.data["dishes"]}  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            [(r["date"], r["total_waste_kg"]) for r in dishes["Chicken rice"]],
            [(datetime.date(2022, 1, 1), 0.2), (datetime.date(2022, 1, 2), 0.4)],
        )
        self.assertEqual(
            [(r["date"], r["total_waste_kg"]) for r in dishes["Noodles"]],
            [(datetime.date(2022, 1, 2), 0.1)],
        )

    def test_only_latest_prediction_per_capture(self) -> None:
        """Test a re-predicted capture counts once, using its newest prediction."""
        capture = Capture.objects.create(image=make_image())
        for bucket in [WasteBucketChoices.ALL, WasteBucketChoices.HALF]:
            Prediction.objects.create(
                capture=capture,
                dish=self.dish,
                waste_bucket=bucket,
                confidence={"dish_name": 0.9, "waste_bucket": 0.9},
                time_taken=1.0,
                model_version="test",
            )
        self.login_admin()
        res = self.client.get(reverse("stats"))

        self.assertEqual(res.data["bowl_count"], 1)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["total_waste_kg"], 0.2)  # pyright: ignore[reportAttributeAccessIssue]

    def test_label_overrides_prediction(self) -> None:
        """Test a human label replaces the prediction's dish and bucket, including for ?dish."""
        noodles = Dish.objects.create(name="Noodles", portion=200, station=self.station)
        capture = Capture.objects.create(image=make_image())
        Prediction.objects.create(
            capture=capture,
            dish=self.dish,
            waste_bucket=WasteBucketChoices.HALF,
            confidence={"dish_name": 0.9, "waste_bucket": 0.9},
            time_taken=1.0,
            model_version="test",
        )
        Label.objects.create(
            capture=capture,
            dish=noodles,
            waste_bucket=WasteBucketChoices.ALL,
            labeler=self.admin,
        )
        self.login_admin()
        res = self.client.get(reverse("stats"))

        self.assertEqual(res.data["bowl_count"], 1)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertAlmostEqual(res.data["total_waste_kg"], 0.2)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(res.data["average_waste_percent"], 100)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(
            [d["dish_name"] for d in res.data["dishes"]],  # pyright: ignore[reportAttributeAccessIssue]
            ["Noodles"],
        )
        self.assertEqual(
            res.data["dishes"][0]["waste_bucket_distribution"],  # pyright: ignore[reportAttributeAccessIssue]
            {WasteBucketChoices.ALL: 1},
        )

        res = self.client.get(reverse("stats"), {"dish": self.dish.pk})
        self.assertEqual(res.data["bowl_count"], 0)  # pyright: ignore[reportAttributeAccessIssue]
        res = self.client.get(reverse("stats"), {"dish": noodles.pk})
        self.assertEqual(res.data["bowl_count"], 1)  # pyright: ignore[reportAttributeAccessIssue]

    def test_invalid_date_filter(self) -> None:
        """Test a malformed ?start returns 400."""
        self.login_admin()
        res = self.client.get(reverse("stats"), {"start": "not-a-date"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
