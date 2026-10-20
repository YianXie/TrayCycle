from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A custom user model that extends the default Django AbstractUser model."""


class Dish(models.Model):
    """A model representing a dish at school during lunch.

    Fields:
        name (CharField): The name of the dish.
        portion (IntegerField): The standard portion size in grams.
        active (BooleanField): A boolean indicating whether the dish is currently being served.
    """

    name = models.CharField(max_length=100)
    portion = models.IntegerField(help_text="Standard portion size in grams")
    active = models.BooleanField(default=True)


class Station(models.Model):
    """A model representing a station at school during lunch.

    Fields:
        name (CharField): The name of the station.
        active (BooleanField): A boolean indicating whether the station is currently open.
    """

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)


class MenuDay(models.Model):
    """A model representing a menu day at school.

    Fields:
        date (DateField): The date of the menu day.
        dishes (ManyToManyField): A many-to-many relationship with the Dish model.
    """

    date = models.DateField()
    dishes = models.ManyToManyField(Dish, through="MenuItem", related_name="menu_days")


class MenuItem(models.Model):
    """A model representing a menu item at school during lunch.

    Fields:
        menu_day (ForeignKey): A foreign key to the MenuDay model.
        dish (ForeignKey): A foreign key to the Dish model.
        station (ForeignKey): A foreign key to the Station model.
    """

    menu_day = models.ForeignKey(
        MenuDay, on_delete=models.CASCADE, related_name="menu_items"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="menu_items")

    station = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="menu_items"
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["menu_day", "station", "dish"], name="unique_menu_item"
            )
        ]


class Device(models.Model):
    """A model representing a device at school during lunch.

    Fields:
        name (CharField): The name of the device.
        location (CharField): The location of the device.
        token (CharField): A unique token for the device.
    """

    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    token = models.CharField(max_length=100, unique=True)


class Capture(models.Model):
    """A model representing a capture of a tray at school during lunch.

    Fields:
        image (ImageField): An image of the tray.
        timestamp (DateTimeField): The timestamp of the capture.
        device (ForeignKey): A foreign key to the Device model.
        source (CharField): A string indicating the source of the capture (camera or upload).
    """

    image = models.ImageField(upload_to="captures/")
    timestamp = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="captures"
    )

    class Sources(models.TextChoices):
        CAMERA = "camera", "Camera"
        UPLOAD = "upload", "Upload"

    source = models.CharField(
        max_length=100, choices=Sources.choices, default=Sources.CAMERA
    )


class Prediction(models.Model):
    """A model representing a prediction of the waste on a tray at school during lunch.

    Fields:
        capture (ForeignKey): A foreign key to the Capture model.
        waste_bucket (IntegerField): A integer indicating the percentage of waste in the tray (0, 25, 50, 75, 100).
        dish (ForeignKey): A foreign key to the Dish model.
        confidence (FloatField): A float indicating the confidence of the prediction.
        model_version (CharField): A string indicating the version of the model used for the prediction
    """

    capture = models.ForeignKey(
        Capture, on_delete=models.CASCADE, related_name="predictions"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="predictions")

    class WasteBucketChoices(models.IntegerChoices):
        NONE = 0
        QUARTER = 25
        HALF = 50
        MOST = 75
        ALL = 100

    waste_bucket = models.IntegerField(
        choices=WasteBucketChoices, default=WasteBucketChoices.NONE
    )

    confidence = models.FloatField()
    model_version = models.CharField(max_length=100)


class Label(models.Model):
    """A model representing a human label of the waste on a tray at school during lunch.

    Fields:
        capture (ForeignKey): A foreign key to the Capture model.
        dish (ForeignKey): A foreign key to the Dish model.
        waste_bucket (IntegerField): A integer indicating the percentage of waste in the tray (0, 25, 50, 75, 100).
        labeler (ForeignKey): A foreign key to the User model representing the user who labeled the capture.
    """

    capture = models.ForeignKey(
        Capture, on_delete=models.CASCADE, related_name="labels"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="labels")

    class WasteBucketChoices(models.IntegerChoices):
        NONE = 0
        SOME = 25
        HALF = 50
        MOST = 75
        ALL = 100

    waste_bucket = models.IntegerField(
        choices=WasteBucketChoices, default=WasteBucketChoices.NONE
    )

    labeler = models.ForeignKey(User, on_delete=models.CASCADE, related_name="labels")


class OverproductionLog(models.Model):
    """A model representing a log of overproduction of a dish at school during lunch.

    Fields:
        date (DateField): The date of the overproduction.
        dish (ForeignKey): A foreign key to the Dish model.
        overproduced_amount (IntegerField): An integer indicating the amount of overproduction in kg
        entered_by (ForeignKey): A foreign key to the User model representing the user who entered
    """

    date = models.DateField()
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name="overproduction_logs"
    )
    overproduced_amount = models.IntegerField(
        help_text="Amount of overproduction in kg"
    )
    entered_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="overproduction_logs"
    )
