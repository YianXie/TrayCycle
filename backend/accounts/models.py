from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """A custom user model that extends the default Django AbstractUser model."""
