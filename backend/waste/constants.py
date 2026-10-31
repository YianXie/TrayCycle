from django.db import models

# Constants for the waste app.
WORKER_GROUP_NAME = "Workers"

# The number of captures to process in a single full batch for the worker.
CAPTURE_CLAIM_BATCH_SIZE = 3

# The maximum number of attempts to process a capture before marking it as failed.
CAPTURE_MAX_ATTEMPTS = 3

# The number of minutes after which a capture is sent back to pending if it has not been processed. This is to prevent captures from being stuck in processing indefinitely.
CAPTURE_TIMEOUT_MINUTES = 3

# The maximum length of the failure_reason field in the Capture model.
CAPTURE_FAILURE_REASON_MAX_LENGTH = 255

# Predictions below this confidence are considered to need review.
CAPTURE_REVIEW_THRESHOLD = 0.75


class WasteBucketChoices(models.IntegerChoices):
    """An enumeration representing the different waste bucket choices."""

    NONE = 0
    SOME = 25
    HALF = 50
    MOST = 75
    ALL = 100


class SourceChoices(models.TextChoices):
    """An enumeration representing the different sources of a capture."""

    CAMERA = "camera", "Camera"
    UPLOAD = "upload", "Upload"


class StatusChoices(models.TextChoices):
    """An enumeration representing the different status choices for a capture."""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"
