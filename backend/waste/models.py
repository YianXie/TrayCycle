import secrets

from django.db import models
from django.utils import timezone

from accounts.models import User

from .constants import (
    CAPTURE_FAILURE_REASON_MAX_LENGTH,
    SourceChoices,
    StatusChoices,
    WasteBucketChoices,
)


class Station(models.Model):
    """A model representing a station at school during lunch.

    Fields:
        name (CharField): The name of the station.
    """

    name = models.CharField(max_length=100, unique=True)
    is_customizable = models.BooleanField()

    def __str__(self) -> str:
        """Return the name of the station as its string representation."""
        return self.name


class Dish(models.Model):
    """A model representing a dish at school during lunch.

    Fields:
        name (CharField): The name of the dish.
        portion (PositiveIntegerfield): The standard portion size in grams.
        station (ForeignKey): A foreign key to the Station model.
    """

    name = models.CharField(max_length=100, unique=True)
    portion = models.PositiveIntegerField(help_text="Standard portion size in grams")
    station = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="dishes"
    )

    def __str__(self) -> str:
        """Return the name of the dish as its string representation."""
        return self.name


class MenuDay(models.Model):
    """A model representing a menu day at school.

    Fields:
        date (DateField): The date of the menu day.
        dishes (ManyToManyField): A many-to-many relationship with the Dish model.
    """

    date = models.DateField(unique=True)
    dishes = models.ManyToManyField(Dish, related_name="menu_days")

    def __str__(self) -> str:
        """Return the date of the menu day as its string representation."""
        return str(self.date)


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
    """A model representing a capture of a bowl at school during lunch.

    Fields:
        image (ImageField): An image of the bowl.
        captured_at (DateTimeField): The timestamp of when the capture was taken.
        received_at (DateTimeField): The timestamp of when the capture was received.
        device (ForeignKey): A foreign key to the Device model, nullable.
        uploaded_by (ForeignKey): A foreign key to the User model, nullable.
        claimed_at (DateTimeField): The timestamp of when the capture was claimed for processing, nullable.
        claimed_by (ForeignKey): A foreign key to the User model representing the worker user that claimed the capture for processing, nullable.
        attempts (PositiveIntegerField): An integer indicating the number of attempts made to process the capture
        source (CharField): A string indicating the source of the capture (camera or upload).
        status (CharField): A string indicating the status of the capture (pending, processing, done, failed).
        failure_reason (CharField): A string indicating the reason for failure, nullable.
    """

    image = models.ImageField(upload_to="captures/")
    captured_at = models.DateTimeField(default=timezone.localtime)
    received_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="captures", null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="captures", null=True, blank=True
    )
    claimed_at = models.DateTimeField(null=True, blank=True)
    claimed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="claimed_captures",
        null=True,
        blank=True,
    )
    attempts = models.PositiveIntegerField(default=0)
    source = models.CharField(
        max_length=100, choices=SourceChoices.choices, default=SourceChoices.CAMERA
    )
    status = models.CharField(
        max_length=100, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    failure_reason = models.CharField(
        max_length=CAPTURE_FAILURE_REASON_MAX_LENGTH, null=True, blank=True
    )

    def __str__(self) -> str:
        """Return a string representation of the capture."""
        return f"{self.received_at} - {self.device} - {self.source} - {self.status}"


class Prediction(models.Model):
    """A model representing a prediction of the waste on a bowl at school during lunch.

    Fields:
        capture (ForeignKey): A foreign key to the Capture model.
        dish (ForeignKey): A foreign key to the Dish model.
        waste_bucket (IntegerField): A integer indicating the percentage of waste in the bowl (0, 25, 50, 75, 100).
        confidence (JSONField): A JSON field containing the confidence values for the dish name and waste bucket predictions, with values between 0 and 1.
        time_taken (FloatField): A float indicating the time taken for the prediction in seconds.
        created_at (DateTimeField): The timestamp of when the prediction was created.
        model_version (CharField): A string indicating the version of the model used for the prediction
    """

    capture = models.ForeignKey(
        Capture, on_delete=models.CASCADE, related_name="predictions"
    )
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="predictions")
    waste_bucket = models.IntegerField(choices=WasteBucketChoices)
    confidence = models.JSONField(default=dict)
    time_taken = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=100)

    class Meta:
        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                condition=models.Q(waste_bucket__in=WasteBucketChoices.values),
                name="prediction_valid_bucket",
            ),
        ]

    def __str__(self) -> str:
        """Return a string representation of the prediction."""
        return f"{self.capture} - {self.dish} - {self.waste_bucket} - {self.confidence} - {self.model_version}"


class Label(models.Model):
    """A model representing a human label of the waste on a bowl at school during lunch.

    Fields:
        capture (ForeignKey): A foreign key to the Capture model.
        dish (ForeignKey): A foreign key to the Dish model.
        waste_bucket (IntegerField): A integer indicating the percentage of waste in the bowl (0, 25, 50, 75, 100).
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
            ),
            models.CheckConstraint(
                condition=models.Q(waste_bucket__in=WasteBucketChoices.values),
                name="label_valid_bucket",
            ),
        ]

    def __str__(self) -> str:
        """Return a string representation of the label."""
        return f"{self.capture} - {self.dish} - {self.waste_bucket} - {self.labeler}"


class OverproductionLog(models.Model):
    """A model representing a log of overproduction of a dish at school during lunch.

    Fields:
        date (DateField): The date of the overproduction.
        dish (ForeignKey): A foreign key to the Dish model.
        overproduced_kg (DecimalField): A decimal indicating the amount of overproduction in kg
        entered_by (ForeignKey): A foreign key to the User model representing the user who entered
    """

    date = models.DateField(default=timezone.localdate)
    dish = models.ForeignKey(
        Dish, on_delete=models.PROTECT, related_name="overproduction_logs"
    )
    overproduced_kg = models.DecimalField(max_digits=6, decimal_places=2)
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
        return f"{self.date} - {self.dish} - {self.overproduced_kg} - {self.entered_by}"
