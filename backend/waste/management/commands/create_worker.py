from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError, CommandParser
from rest_framework.authtoken.models import Token

from waste.constants import WORKER_GROUP_NAME


class Command(BaseCommand):
    """A custom Django management command to create a worker user and generate an authentication token."""

    help = "Create a new worker user with the given username, add it to the Workers group, and print the token once."

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command-line arguments for the management command.

        Args:
            parser (CommandParser): The argument parser to which the command-line arguments will be added.
        """
        parser.add_argument(
            "--username",
            type=str,
            default="inference-worker-1",
            help="Username for the new worker user.",
        )
        parser.add_argument(
            "--group",
            type=str,
            default=WORKER_GROUP_NAME,
            help="Group to which the new worker user will be added.",
        )
        parser.add_argument(
            "--rotate-token",
            action="store_true",
            help="Rotate the token for the existing user if it already exists.",
        )

    def handle(self, *args, **options) -> None:
        """Handle the command to create a worker user and generate an authentication token.

        Raises:
            CommandError: If the specified group does not exist.
        """
        # Get the username and group name from the command-line arguments
        username = options["username"]
        group_name = options["group"]
        rotate_token = options["rotate_token"]

        # Check if the group exists
        group = Group.objects.filter(name=group_name).first()
        if group is None:
            raise CommandError(f"Group '{group_name}' does not exist.")

        # Check if the user already exists, if not, create the user and add to the group
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        created = False
        if user is None:
            user = User.objects.create_user(username=username)
            created = True
        elif user is not None and user.is_staff or user.is_superuser:
            raise CommandError(
                f"User '{username}' already exists and is a staff or superuser. Cannot create a worker user with the same username."
            )
        user.is_staff = False
        user.is_superuser = False
        user.set_unusable_password()
        user.save()

        # Add the user to the group and create a token for the user
        user.groups.add(group)
        if not created and rotate_token:
            Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)

        # Output the token to the console
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created worker user '{username}'. Token: {token.key}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' already exists. Token: {token.key}"
                )
            )
