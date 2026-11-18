from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from waste.models import Dish, MenuDay

from .shared import IN_MEMORY_STORAGE, WasteAPITestCase


@override_settings(STORAGES=IN_MEMORY_STORAGE)
class MenuDayAPITests(WasteAPITestCase):
    """Basic CRUD plus permission checks for the MenuDay API."""

    def test_admin_can_create(self) -> None:
        """Test staff members can create a MenuDay via PUT and the response echoes it back."""
        self.login_admin()
        res = self.client.put(
            reverse("menuday-detail", kwargs={"date": "2024-01-01"}),
            {"items": [{"dish": self.dish.id}]},  # pyright: ignore[reportAttributeAccessIssue]
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # pyright: ignore[reportAttributeAccessIssue]
        menu_day = MenuDay.objects.get(pk=res.data["id"])  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(menu_day.dishes.get(), self.dish)
        self.assertTrue(MenuDay.objects.filter(date="2024-01-01").exists())

    def test_invalid_date_raises(self) -> None:
        """Test that an invalid date format returns a 400 error."""
        self.login_admin()
        for bad_date in ("invalid-date", "2024-13-01"):
            res = self.client.put(
                reverse("menuday-detail", kwargs={"date": bad_date}),
                {"items": [{"dish": self.dish.id}]},  # pyright: ignore[reportAttributeAccessIssue]
                format="json",
            )
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
            self.assertIn("date", res.data)  # pyright: ignore[reportAttributeAccessIssue]

    def test_update_replace_menu_day(self) -> None:
        """Test that updating a MenuDay replaces the existing dishes."""
        self.login_admin()
        new_dish = Dish.objects.create(
            name="Veggie stir fry", portion=350, station=self.station
        )
        # Update the existing MenuDay to a new dish
        res = self.client.put(
            reverse(
                "menuday-detail",
                kwargs={"date": "2022-01-01"},
            ),
            {"items": [{"dish": new_dish.pk}]},  # pyright: ignore[reportAttributeAccessIssue]
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # pyright: ignore[reportAttributeAccessIssue]
        menu_day = MenuDay.objects.get(date="2022-01-01")
        self.assertEqual(
            list(menu_day.dishes.all()),
            [Dish.objects.get(pk=new_dish.pk)],  # pyright: ignore[reportAttributeAccessIssue]
        )

    def test_duplicate_date_rejected(self) -> None:
        """Test MenuDay.date is unique, so a duplicate returns 400."""
        self.login_admin()
        res = self.client.post(
            reverse("menuday-list"),
            {"date": self.menu_day.date, "dishes": [self.dish.id]},  # pyright: ignore[reportAttributeAccessIssue]
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAttributeAccessIssue]
        self.assertIn("date", res.data)  # pyright: ignore[reportAttributeAccessIssue]
