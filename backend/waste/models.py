import secrets

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WasteBucketChoices(models.IntegerChoices):
    NONE = 0
    SOME = 25
    HALF = 50
    MOST = 75
    ALL = 100


class User(AbstractUser):
    """A custom user model that extends the default Django AbstractUser model."""


class Dish(models.Model):
    """A model representing a dish at school during lunch.

    Fields:
        name (CharField): The name of the dish.
        portion (PositiveIntegerfield): The standard portion size in grams.
        active (BooleanField): A boolean indicating whether the dish is currently being served.
    """

    name = models.CharField(max_length=100, unique=True)
    portion = models.PositiveIntegerField(help_text="Standard portion size in grams")
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Return the name of the dish as its string representation."""
        return self.name


class Compartment(models.Model):
    """A model representing a tray compartment.

    Fields:
        name (CharField): The name of the compartment.
        active (BooleanField): A boolean indicating whether the compartment is currently open.
    """

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        """Return the name of the compartment as its string representation."""
        return self.name


class MenuDay(models.Model):
    """A model representing a menu day at school.

    Fields:
        date (DateField): The date of the menu day.
        dishes (ManyToManyField): A many-to-many relationship with the Dish model.
    """

    date = models.DateField(unique=True)
    dishes = models.ManyToManyField(Dish, through="MenuItem", related_name="menu_days")

    def __str__(self) -> str:
        """Return the date of the menu day as its string representation."""
        return str(self.date)


class MenuItem(models.Model):
    """A model representing a menu item at school during lunch.

    Fields:
        menu_day (ForeignKey): A foreign key to the MenuDay model.
        dish (ForeignKey): A foreign key to the Dish model.
        compartment (ForeignKey): A foreign key to the Compartment model.
    """

    menu_day = models.ForeignKey(
        MenuDay, on_delete=models.CASCADE, related_name="menu_items"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="menu_items")

    compartment = models.ForeignKey(
        Compartment, on_delete=models.PROTECT, related_name="menu_items"
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["menu_day", "compartment"], name="unique_menu_compartment"
            ),
            models.UniqueConstraint(
                fields=["menu_day", "dish"], name="unique_menu_dish"
            ),
        ]

    def __str__(self) -> str:
        """Return a string representation of the menu item."""
        return f"{self.menu_day} - {self.dish} - {self.compartment}"


class Device(models.Model):
    """A model representing a device at school during lunch.

    Fields:
        name (CharField): The name of the device.
        location (CharField): The location of the device.
        token (CharField): A unique token for the device.
    """

    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    token = models.CharField(
        max_length=100, unique=True, editable=False, default=secrets.token_urlsafe
    )

    def __str__(self) -> str:
        """Return a string representation of the device."""
        return f"{self.name} - {self.location}"


class Capture(models.Model):
    """A model representing a capture of a tray at school during lunch.

    Fields:
        image (ImageField): An image of the tray.
        captured_at (DateTimeField): The timestamp of when the capture was taken.
        received_at (DateTimeField): The timestamp of when the capture was received.
        device (ForeignKey): A foreign key to the Device model, nullable.
        uploaded_by (ForeignKey): A foreign key to the User model, nullable.
        source (CharField): A string indicating the source of the capture (camera or upload).
        status (CharField): A string indicating the status of the capture (pending, processing, done, failed).
    """

    image = models.ImageField(upload_to="captures/")
    captured_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="captures", null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="captures", null=True, blank=True
    )

    class Sources(models.TextChoices):
        CAMERA = "camera", "Camera"
        UPLOAD = "upload", "Upload"

    source = models.CharField(
        max_length=100, choices=Sources.choices, default=Sources.CAMERA
    )

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    status = models.CharField(
        max_length=100, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )

    def __str__(self) -> str:
        """Return a string representation of the capture."""
        return f"{self.received_at} - {self.device} - {self.source} - {self.status}"


class Prediction(models.Model):
    """A model representing a prediction of the waste on a tray at school during lunch.

    Fields:
        capture (ForeignKey): A foreign key to the Capture model.
        waste_bucket (IntegerField): A integer indicating the percentage of waste in the tray (0, 25, 50, 75, 100).
        dish (ForeignKey): A foreign key to the Dish model.
        confidence (FloatField): A float indicating the confidence of the prediction.
        created_at (DateTimeField): The timestamp of when the prediction was created.
        model_version (CharField): A string indicating the version of the model used for the prediction
    """

    capture = models.ForeignKey(
        Capture, on_delete=models.CASCADE, related_name="predictions"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="predictions")
    waste_bucket = models.IntegerField(choices=WasteBucketChoices)
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=100)

    def __str__(self) -> str:
        """Return a string representation of the prediction."""
        return f"{self.capture} - {self.dish} - {self.waste_bucket} - {self.confidence} - {self.model_version}"


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
    waste_bucket = models.IntegerField(choices=WasteBucketChoices)
    labeler = models.ForeignKey(User, on_delete=models.PROTECT, related_name="labels")

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["capture", "dish", "labeler"], name="unique_label"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of the label."""
        return f"{self.capture} - {self.dish} - {self.waste_bucket} - {self.labeler}"


class OverproductionLog(models.Model):
    """A model representing a log of overproduction of a dish at school during lunch.

    Fields:
        date (DateField): The date of the overproduction.
        dish (ForeignKey): A foreign key to the Dish model.
        overproduced_amount (DecimalField): A decimal indicating the amount of overproduction in kg
        entered_by (ForeignKey): A foreign key to the User model representing the user who entered
    """

    date = models.DateField()
    dish = models.ForeignKey(
        Dish, on_delete=models.PROTECT, related_name="overproduction_logs"
    )
    overproduced_amount = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Amount of overproduction in kg"
    )
    entered_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="overproduction_logs"
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["date", "dish"], name="unique_overproduction_log"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of the overproduction log."""
        return f"{self.date} - {self.dish} - {self.overproduced_amount} - {self.entered_by}"
