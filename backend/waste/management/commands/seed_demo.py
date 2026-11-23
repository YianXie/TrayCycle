from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.core.management.color import no_style
from django.db import connection, transaction

from accounts.models import User
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
)

DEMO_IMAGES_DIR = Path(__file__).resolve().parent / "demo_images"


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

    def load_image(self, filename: str) -> SimpleUploadedFile:
        """Build a tiny valid jpg so ImageField validation passes.

        Args:
            name (str): file name for the upload.

        Returns:
            SimpleUploadedFile: an in-memory image file.
        """
        path = DEMO_IMAGES_DIR / filename
        if not path.is_file():
            raise CommandError(f"Demo image not found: {path}")
        return ContentFile(path.read_bytes(), name=path.name)  # pyright: ignore[reportReturnType]

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
                    for c in Capture.objects.all():
                        if c.image:
                            c.image.delete(save=False)
                    Capture.objects.all().delete()
                    MenuDay.objects.all().delete()
                    Device.objects.all().delete()
                    Dish.objects.all().delete()
                    Station.objects.all().delete()
                    User.objects.all().delete()

        # Reset the database sequences for the relevant models to ensure primary keys start from 1
        statements = connection.ops.sequence_reset_sql(
            no_style(),
            [
                User,
                Station,
                Dish,
                MenuDay,
                Device,
                Capture,
                Prediction,
                Label,
                OverproductionLog,
            ],
        )
        if statements:
            with connection.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
                self.stdout.write(
                    self.style.SUCCESS("Database sequences reset successfully.")
                )
        else:
            self.stdout.write(self.style.WARNING("No database sequences to reset."))

        # Define the demo data
        users = [
            {
                "username": "Admin 1",
                "password": settings.ADMIN_1_PASSWORD,
                "is_staff": True,
            },
            {
                "username": "Admin 2",
                "password": settings.ADMIN_2_PASSWORD,
                "is_staff": True,
            },
            {
                "username": "inference-worker-1",
                "is_worker": True,
            },
            {
                "username": "inference-worker-2",
                "is_worker": True,
            },
        ]
        stations = [
            {
                "name": "Asian cuisine",
                "is_customizable": True,
            },
            {
                "name": "Salad bar",
                "is_customizable": True,
            },
            {
                "name": "Chicken rice station",
                "is_customizable": False,
            },
        ]
        dishes = [
            {
                "name": "Chicken Teriyaki",
                "station": "Asian cuisine",
                "portion": 250,
            },
            {
                "name": "Beef Bulgogi",
                "station": "Asian cuisine",
                "portion": 350,
            },
            {
                "name": "Sweet and sour pork",
                "station": "Asian cuisine",
                "portion": 300,
            },
            {
                "name": "Caesar Salad",
                "station": "Salad bar",
                "portion": 200,
            },
            {
                "name": "Greek Salad",
                "station": "Salad bar",
                "portion": 250,
            },
            {
                "name": "Hainanese Chicken Rice",
                "station": "Chicken rice station",
                "portion": 400,
            },
        ]
        menu_days = [
            {
                "date": "2025-12-01",
                "dishes": [
                    "Chicken Teriyaki",
                    "Caesar Salad",
                    "Hainanese Chicken Rice",
                ],
            },
            {
                "date": "2025-12-02",
                "dishes": [
                    "Beef Bulgogi",
                    "Greek Salad",
                    "Hainanese Chicken Rice",
                ],
            },
            {
                "date": "2025-12-03",
                "dishes": [
                    "Sweet and sour pork",
                    "Caesar Salad",
                    "Hainanese Chicken Rice",
                ],
            },
            {
                "date": "2025-12-04",
                "dishes": [
                    "Chicken Teriyaki",
                    "Greek Salad",
                    "Hainanese Chicken Rice",
                ],
            },
            {
                "date": "2025-12-05",
                "dishes": [
                    "Beef Bulgogi",
                    "Caesar Salad",
                    "Hainanese Chicken Rice",
                ],
            },
        ]
        devices = [
            {
                "name": "Cam 1",
                "location": "Cafe A",
            },
            {
                "name": "Cam 2",
                "location": "Cafe B",
            },
        ]
        # Captures have no natural unique field, so they are keyed by a reference name for predictions
        captures = {
            "capture1": {
                "image": self.load_image("capture1.jpg"),
                "captured_at": "2025-12-01T12:00:00Z",
                "device": "Cam 1",
                "uploaded_by": None,
                "claimed_at": "2025-12-01T12:01:00Z",
                "claimed_by": "inference-worker-1",
                "attempts": 1,
                "source": SourceChoices.CAMERA,
                "status": StatusChoices.DONE,
            },
            "capture2": {
                "image": self.load_image("capture2.jpg"),
                "captured_at": "2025-12-02T11:29:43Z",
                "device": "Cam 2",
                "uploaded_by": None,
                "claimed_at": "2025-12-02T11:29:47Z",
                "claimed_by": "inference-worker-2",
                "attempts": 2,
                "source": SourceChoices.CAMERA,
                "status": StatusChoices.DONE,
            },
            "capture3": {
                "image": self.load_image("capture3.jpg"),
                "captured_at": "2025-12-03T11:42:03Z",
                "device": None,
                "uploaded_by": "Admin 1",
                "claimed_at": "2025-12-03T11:44:02Z",
                "claimed_by": "inference-worker-1",
                "attempts": 1,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.DONE,
            },
            "capture4": {
                "image": self.load_image("capture4.jpg"),
                "captured_at": "2025-12-04T12:01:59Z",
                "device": None,
                "uploaded_by": "Admin 2",
                "claimed_at": "2025-12-04T12:02:12Z",
                "claimed_by": "inference-worker-1",
                "attempts": 3,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.FAILED,
            },
            "capture5": {
                "image": self.load_image("capture5.jpg"),
                "captured_at": "2025-12-05T12:03:22Z",
                "device": None,
                "uploaded_by": "Admin 1",
                "claimed_at": "2025-12-05T12:03:24Z",
                "claimed_by": "inference-worker-2",
                "attempts": 1,
                "source": SourceChoices.UPLOAD,
                "status": StatusChoices.DONE,
            },
        }
        predictions = [
            {
                "capture": "capture1",
                "dish": "Chicken Teriyaki",
                "waste_bucket": 25,
                "confidence": 0.85,
                "model_version": "1.0",
            },
            {
                "capture": "capture2",
                "dish": "Caesar Salad",
                "waste_bucket": 0,
                "confidence": 0.7,
                "model_version": "1.0",
            },
            {
                "capture": "capture3",
                "dish": "Beef Bulgogi",
                "waste_bucket": 75,
                "confidence": 0.35,
                "model_version": "1.0",
            },
            {
                "capture": "capture4",
                "dish": "Hainanese Chicken Rice",
                "waste_bucket": 50,
                "confidence": 0.97,
                "model_version": "1.0",
            },
            {
                "capture": "capture5",
                "dish": "Sweet and sour pork",
                "waste_bucket": 25,
                "confidence": 0.9,
                "model_version": "1.0",
            },
        ]

        # Create the objects in the database, letting the database assign primary keys.
        # Related objects are looked up by name from the objects created earlier.
        user_objs = {}
        for user_data in users:
            if user_data.get("is_worker"):
                worker = User.objects.create_user(
                    username=user_data["username"],
                )
                worker.set_unusable_password()
                worker.groups.add(Group.objects.get(name=WORKER_GROUP_NAME))
                user_objs[worker.username] = worker
            else:
                user = User.objects.create_user(**user_data)
                user_objs[user.username] = user

        station_objs = {}
        for station_data in stations:
            station = Station.objects.create(**station_data)
            station_objs[station.name] = station

        dish_objs = {}
        for dish_data in dishes:
            dish = Dish.objects.create(
                **{**dish_data, "station": station_objs[dish_data["station"]]}
            )
            dish_objs[dish.name] = dish

        for menu_day_data in menu_days:
            menu_day = MenuDay.objects.create(date=menu_day_data["date"])
            menu_day.dishes.set([dish_objs[name] for name in menu_day_data["dishes"]])

        device_objs = {}
        for device_data in devices:
            device = Device.objects.create(**device_data)
            device_objs[device.name] = device

        capture_objs = {}
        for ref, capture_data in captures.items():
            capture_objs[ref] = Capture.objects.create(
                **{
                    **capture_data,
                    "device": device_objs.get(capture_data["device"]),
                    "uploaded_by": user_objs.get(capture_data["uploaded_by"]),
                    "claimed_by": user_objs.get(capture_data["claimed_by"]),
                }
            )

        for prediction_data in predictions:
            Prediction.objects.create(
                **{
                    **prediction_data,
                    "capture": capture_objs[prediction_data["capture"]],
                    "dish": dish_objs[prediction_data["dish"]],
                }
            )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
