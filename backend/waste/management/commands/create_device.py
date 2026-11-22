from django.core.management.base import BaseCommand, CommandParser

from waste.models import Device


class Command(BaseCommand):
    """A custom Django management command to create a device and generate an authentication token."""

    help = "Create a new device with the given name and location, and print the token once."

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command-line arguments for the management command.

        Args:
            parser (CommandParser): The argument parser to which the command-line arguments will be added.
        """
        parser.add_argument(
            "--name",
            type=str,
            help="Name for the new device.",
        )
        parser.add_argument(
            "--location",
            type=str,
            help="Location of the new device.",
        )
        parser.add_argument(
            "--rotate-token",
            action="store_true",
            help="Rotate the token for the existing device if it already exists.",
        )

    def handle(self, *args, **options) -> None:
        """Handle the command to create a device and generate an authentication token.

        Raises:
            CommandError: If the specified group does not exist.
        """
        # Get the name, location, whether to rotate the token from the command-line arguments
        name = options["name"]
        location = options["location"]
        rotate_token = options["rotate_token"]

        if not name or not location:
            self.stdout.write(
                self.style.ERROR("Both --name and --location arguments are required.")
            )
            return

        device, created = Device.objects.get_or_create(name=name, location=location)
        if not created and rotate_token:
            device.token = None  # pyright: ignore[reportAttributeAccessIssue]
            device.save()

        # Output the token to the console
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created device '{name}'. Token: {device.token}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Device '{name}' already exists. Token: {device.token}"
                )
            )
