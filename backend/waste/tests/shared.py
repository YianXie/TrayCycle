from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient, APITestCase

from waste.models import (
    Device,
    Dish,
    MenuDay,
    Station,
    User,
)

IN_MEMORY_STORAGE = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def make_image(name: str = "bowl.png") -> SimpleUploadedFile:
    """Build a tiny valid PNG so ImageField validation passes.

    Args:
        name (str): file name for the upload.

    Returns:
        SimpleUploadedFile: an in-memory image file.
    """
    buf = BytesIO()
    Image.new("RGB", (10, 10), "white").save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class WasteAPITestCase(APITestCase):
    """Base class with shared fixtures for all waste API tests."""

    client: APIClient  # pyright: ignore[reportIncompatibleVariableOverride]

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up a few shared objects for all tests in this class."""
        cls.admin = User.objects.create_user("admin", password="pw", is_staff=True)
        cls.student = User.objects.create_user("student", password="pw")
        cls.station = Station.objects.create(name="Asian", is_customizable=False)
        cls.dish = Dish.objects.create(
            name="Chicken rice", portion=400, station=cls.station
        )
        cls.menu_day = MenuDay.objects.create(date="2022-01-01")
        cls.menu_day.dishes.set([cls.dish])
        cls.device = Device.objects.create(name="cam-1", location="Cafe A")

    def login_admin(self) -> None:
        """Authenticate the test client as a staff user, skipping token auth."""
        self.client.force_authenticate(user=self.admin)  # pyright: ignore[reportAttributeAccessIssue]

    def login_student(self) -> None:
        """Authenticate the test client as a non-staff user, skipping token auth."""
        self.client.force_authenticate(user=self.student)  # pyright: ignore[reportAttributeAccessIssue]
