from io import BytesIO

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from PIL import Image

from waste.constants import WORKER_GROUP_NAME, SourceChoices, StatusChoices
from waste.models import (
    Capture,
    Device,
    Dish,
    Label,
    MenuDay,
    OverproductionLog,
    Prediction,
    Station,
    User,
)


class Command(BaseCommand):
    """A custom Django management command to create one week of demo data for the application."""

    help = "Create one week of demo data for the application."

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command-line arguments for the management command.

        Args:
            parser (CommandParser): The argument parser to which the command-line arguments will be added.
        """
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force the creation of demo data even if it already exists. Replace existing data.",
        )

    def make_image(self, name: str = "bowl.png") -> SimpleUploadedFile:
        """Build a tiny valid PNG so ImageField validation passes.

        Args:
            name (str): file name for the upload.

        Returns:
            SimpleUploadedFile: an in-memory image file.
        """
        buf = BytesIO()
        Image.new("RGB", (10, 10), "white").save(buf, format="PNG")
        return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")

    def handle(self, *args, **options) -> None:
        # Read the --force option from the command-line arguments
        force = options["force"]

        # Check if any of the relevant models already have data in the database
        if (
            User.objects.exists()
            or Station.objects.exists()
            or Dish.objects.exists()
            or MenuDay.objects.exists()
            or Device.objects.exists()
            or Capture.objects.exists()
            or Prediction.objects.exists()
            or Label.objects.exists()
            or OverproductionLog.objects.exists()
        ):
            if not force:
                raise CommandError(
                    "Database data already exists. Use --force to replace existing data."
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Database data already exists. Replacing existing data."
                    )
                )
                with transaction.atomic():
                    # Delete existing data in the correct order to avoid foreign key constraint violations
                    Label.objects.all().delete()
                    OverproductionLog.objects.all().delete()
                    Prediction.objects.all().delete()
                    Capture.objects.all().delete()
                    MenuDay.objects.all().delete()
                    Device.objects.all().delete()
                    Dish.objects.all().delete()
                    Station.objects.all().delete()
                    User.objects.all().delete()

        # Define the demo data
        users = [
            {
                "id": 1,
                "username": "Admin 1",
                "password": "pw",
                "is_staff": True,
            },
            {
                "id": 2,
                "username": "Admin 2",
                "password": "pw",
                "is_staff": True,
            },
            {
                "id": 3,
                "username": "inference-worker-1",
                "password": "pw",
                "is_worker": True,
            },
            {
                "id": 4,
                "username": "inference-worker-2",
                "password": "pw",
                "is_worker": True,
            },
        ]
        stations = [
            {
                "id": 1,
                "name": "Asian cuisine",
                "is_customizable": True,
            },
            {
                "id": 2,
                "name": "Salad bar",
                "is_customizable": True,
            },
            {
                "id": 3,
                "name": "Chicken rice station",
                "is_customizable": False,
            },
        ]
        dishes = [
            {
                "id": 1,
                "name": "Chicken Teriyaki",
                "station_id": 1,
                "portion": 250,
            },
            {
                "id": 2,
                "name": "Beef Bulgogi",
                "station_id": 1,
                "portion": 350,
            },
            {
                "id": 3,
                "name": "Sweet and sour pork",
                "station_id": 1,
                "portion": 300,
            },
            {
                "id": 4,
                "name": "Caesar Salad",
                "station_id": 2,
                "portion": 200,
            },
            {
                "id": 5,
                "name": "Greek Salad",
                "station_id": 2,
                "portion": 250,
            },
            {
                "id": 6,
                "name": "Hainanese Chicken Rice",
                "station_id": 3,
                "portion": 400,
            },
        ]
        menu_days = [
            {
                "date": "2025-12-01",
                "dishes": [1, 4, 6],
            },
            {
                "date": "2025-12-02",
                "dishes": [2, 5, 6],
            },
            {
                "date": "2025-12-03",
                "dishes": [3, 4, 6],
            },
            {
                "date": "2025-12-04",
                "dishes": [1, 5, 6],
            },
            {
                "date": "2025-12-05",
                "dishes": [2, 4, 6],
            },
        ]
        devices = [
            {
                "id": 1,
                "name": "Cam 1",
                "location": "Cafe A",
            },
            {
                "id": 2,
                "name": "Cam 2",
                "location": "Cafe B",
            },
        ]
        captures = [
            {
                "id": 1,
                "image": self.make_image("capture1.png"),
                "captured_at": "2025-12-01T12:00:00Z",
                "device_id": 1,
                "uploaded_by_id": None,
                "claimed_at": "2025-12-01T12:01:00Z",
                "claimed_by_id": 3,
                "attempts": 1,
                "source": SourceChoices.CAMERA,
                "status": StatusChoices.DONE,
            },
            {
                "id": 2,
                "image": self.make_image("capture2.png"),
                "captured_at": "2025-12-02T11:29:43Z",
                "device_id": 2,
                "uploaded_by_id": None,
                "claimed_at": "2025-12-02T11:29:47Z",
                "claimed_by_id": 4,
                "attempts": 2,
                "source": SourceChoices.CAMERA,
                "status": StatusChoices.DONE,
            },
            {
                "id": 3,
                "image": self.make_image("capture3.png"),
                "captured_at": "2025-12-03T11:42:03Z",
                "device_id": None,
                "uploaded_by_id": 1,
                "claimed_at": "2025-12-03T11:44:02Z",
                "claimed_by_id": 3,
                "attempts": 1,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.DONE,
            },
            {
                "id": 4,
                "image": self.make_image("capture4.png"),
                "captured_at": "2025-12-04T12:01:59Z",
                "device_id": None,
                "uploaded_by_id": 2,
                "claimed_at": "2025-12-04T12:02:12Z",
                "claimed_by_id": 3,
                "attempts": 3,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.FAILED,
            },
            {
                "id": 5,
                "image": self.make_image("capture5.png"),
                "captured_at": "2025-12-05T12:03:22Z",
                "device_id": None,
                "uploaded_by_id": 1,
                "claimed_at": "2025-12-05T12:03:24Z",
                "claimed_by_id": 4,
                "attempts": 1,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.DONE,
            },
        ]
        predictions = [
            {
                "id": 1,
                "capture_id": 1,
                "dish_id": 1,
                "waste_bucket": 25,
                "confidence": 0.85,
                "model_version": "1.0",
            },
            {
                "id": 2,
                "capture_id": 2,
                "dish_id": 4,
                "waste_bucket": 0,
                "confidence": 0.7,
                "model_version": "1.0",
            },
            {
                "id": 3,
                "capture_id": 3,
                "dish_id": 2,
                "waste_bucket": 75,
                "confidence": 0.35,
                "model_version": "1.0",
            },
            {
                "id": 4,
                "capture_id": 4,
                "dish_id": 6,
                "waste_bucket": 50,
                "confidence": 0.97,
                "model_version": "1.0",
            },
            {
                "id": 5,
                "capture_id": 5,
                "dish_id": 3,
                "waste_bucket": 25,
                "confidence": 0.9,
                "model_version": "1.0",
            },
        ]

        # Create the objects in the database
        for user_data in users:
            if user_data.get("is_worker"):
                worker = User.objects.create_user(
                    id=user_data["id"],
                    username=user_data["username"],
                    password=user_data["password"],
                )
                worker.groups.add(Group.objects.get(name=WORKER_GROUP_NAME))
            else:
                User.objects.create_user(**user_data)

        for station_data in stations:
            Station.objects.create(**station_data)

        for dish_data in dishes:
            Dish.objects.create(**dish_data)

        for menu_day_data in menu_days:
            menu_day = MenuDay.objects.create(date=menu_day_data["date"])
            menu_day.dishes.set(menu_day_data["dishes"])

        for device_data in devices:
            Device.objects.create(**device_data)

        for capture_data in captures:
            Capture.objects.create(**capture_data)

        for prediction_data in predictions:
            Prediction.objects.create(**prediction_data)

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
