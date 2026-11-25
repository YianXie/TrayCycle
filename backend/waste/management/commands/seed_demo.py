import random
from datetime import datetime, time, timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile  # noqa: F401
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.core.management.color import no_style
from django.db import connection, transaction
from django.utils import timezone
from PIL import Image

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
        parser.add_argument(
            "--days",
            type=int,
            default=14,
            help="Days of demo data, ending today.",
        )
        parser.add_argument(
            "--captures-per-day",
            type=int,
            default=12,
            help="Captures to create per day.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=2026,
            help="Random seed so runs are reproducible.",
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

    # def load_image(self, filename: str) -> SimpleUploadedFile:
    #     """Build a tiny valid jpg so ImageField validation passes.

    #     Args:
    #         name (str): file name for the upload.

    #     Returns:
    #         SimpleUploadedFile: an in-memory image file.
    #     """
    #     path = DEMO_IMAGES_DIR / filename
    #     if not path.is_file():
    #         raise CommandError(f"Demo image not found: {path}")
    #     return ContentFile(path.read_bytes(), name=path.name)  # pyright: ignore[reportReturnType]

    # Create demo data for the application, replacing existing data if --force is specified.
    BUCKETS = (0, 25, 50, 75, 100)

    def build_schedule(self, days: int, per_day: int, dish_names: list[str]):
        """Generate menu days, captures, predictions and labels for days ending today."""
        rng = random.Random(self.seed)
        today = timezone.localdate()
        menu_days: list[dict] = []
        captures: dict[str, dict] = {}
        predictions: list[dict] = []
        labels: list[dict] = []

        for offset in range(days):
            date = today - timedelta(days=days - 1 - offset)
            served = rng.sample(dish_names, k=rng.choice([3, 4, 4, 5]))
            menu_days.append({"date": date, "dishes": served})

            progress = offset / max(days - 1, 1)
            weights = [2 + 5 * progress, 5, 4, 2, 1]

            for index in range(per_day):
                key = f"capture{date:%Y%m%d}-{index + 1}"
                dish = rng.choice(served)
                bucket = rng.choices(self.BUCKETS, weights=weights)[0]
                captured_at = timezone.make_aware(
                    datetime.combine(
                        date,
                        time(
                            hour=rng.choice([11, 12, 12, 13]),
                            minute=rng.randrange(60),
                        ),
                    )
                )
                failed = rng.random() < 0.02
                uploaded = rng.random() < 0.3

                captures[key] = {
                    "image": self.make_image(f"{key}.png"),
                    "captured_at": captured_at,
                    "device": None if uploaded else rng.choice(["Cam 1", "Cam 2"]),
                    "uploaded_by": "Admin 1" if uploaded else None,
                    "claimed_at": captured_at
                    + timedelta(seconds=rng.randrange(5, 120)),
                    "claimed_by": rng.choice(
                        ["inference-worker-1", "inference-worker-2"]
                    ),
                    "attempts": 3 if failed else 1,
                    "source": SourceChoices.UPLOAD
                    if uploaded
                    else SourceChoices.CAMERA,
                    "status": StatusChoices.FAILED if failed else StatusChoices.DONE,
                }

                if failed:
                    continue

                predictions.append(
                    {
                        "capture": key,
                        "dish": dish,
                        "waste_bucket": bucket,
                        "confidence": {
                            "dish_name": round(rng.uniform(0.35, 0.99), 2),
                            "waste_bucket": round(rng.uniform(0.35, 0.99), 2),
                        },
                        "time_taken": rng.random() * 2.0,
                        "model_version": "1.0",
                    }
                )

        return menu_days, captures, predictions, labels

    def handle(self, *args, **options) -> None:
        # Read the --force option from the command-line arguments
        force = options["force"]
        options["days"]
        options["captures_per_day"]
        options["seed"]

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
        self.seed = options["seed"]
        menu_days, captures, predictions, labels = self.build_schedule(
            days=options["days"],
            per_day=options["captures_per_day"],
            dish_names=[dish["name"] for dish in dishes],
        )

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
        for label_data in labels:
            Label.objects.create(
                **{
                    **label_data,
                    "capture": capture_objs[label_data["capture"]],
                    "dish": dish_objs[label_data["dish"]],
                    "labeler": user_objs[label_data["labeler"]],
                }
            )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
