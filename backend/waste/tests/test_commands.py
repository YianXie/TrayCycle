from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from rest_framework.authtoken.models import Token

from waste.constants import WORKER_GROUP_NAME
from waste.models import User


class CreateWorkerCommandTests(TestCase):
    """Tests for the create_worker management command."""

    def run_command(self, *args: str) -> str:
        """Run create_worker with the given arguments and return its output.

        Args:
            *args (str): command-line arguments for the command.

        Returns:
            str: everything the command wrote to stdout.
        """
        out = StringIO()
        call_command("create_worker", *args, stdout=out)
        return out.getvalue()

    def test_creates_new_worker(self) -> None:
        """Test that a new user is created in the Workers group with an unusable password and a token."""
        output = self.run_command("--username", "worker-1")

        user = User.objects.get(username="worker-1")
        self.assertTrue(user.groups.filter(name=WORKER_GROUP_NAME).exists())
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Token.objects.get(user=user).key, output)

    def test_refuses_existing_non_worker_user(self) -> None:
        """Test that an existing regular user is not converted into a worker."""
        user = User.objects.create_user("alice", password="pw")

        with self.assertRaises(CommandError):
            self.run_command("--username", "alice")

        user.refresh_from_db()
        self.assertTrue(user.check_password("pw"))
        self.assertFalse(user.groups.filter(name=WORKER_GROUP_NAME).exists())
        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_refuses_existing_staff_user(self) -> None:
        """Test that an existing staff user is not converted into a worker."""
        user = User.objects.create_user("boss", password="pw", is_staff=True)

        with self.assertRaises(CommandError):
            self.run_command("--username", "boss")

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("pw"))

    def test_refuses_existing_superuser(self) -> None:
        """Test that an existing non-staff superuser is not converted into a worker."""
        user = User.objects.create_user("root", password="pw", is_superuser=True)

        with self.assertRaises(CommandError):
            self.run_command("--username", "root")

        user.refresh_from_db()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("pw"))

    def test_rerun_for_existing_worker_keeps_token(self) -> None:
        """Test that re-running the command for an existing worker prints the same token."""
        self.run_command("--username", "worker-1")
        token_key = Token.objects.get(user__username="worker-1").key

        output = self.run_command("--username", "worker-1")

        self.assertEqual(Token.objects.get(user__username="worker-1").key, token_key)
        self.assertIn(token_key, output)

    def test_rotate_token_for_existing_worker(self) -> None:
        """Test that --rotate-token replaces an existing worker's token."""
        self.run_command("--username", "worker-1")
        old_key = Token.objects.get(user__username="worker-1").key

        output = self.run_command("--username", "worker-1", "--rotate-token")

        new_key = Token.objects.get(user__username="worker-1").key
        self.assertNotEqual(new_key, old_key)
        self.assertIn(new_key, output)

    def test_missing_group_raises(self) -> None:
        """Test that the command fails without creating a user when the group does not exist."""
        with self.assertRaises(CommandError):
            self.run_command("--username", "worker-1", "--group", "No such group")

        self.assertFalse(User.objects.filter(username="worker-1").exists())

    def test_custom_group(self) -> None:
        """Test that the worker is added to the group passed with --group."""
        Group.objects.create(name="Night shift")

        self.run_command("--username", "worker-1", "--group", "Night shift")

        user = User.objects.get(username="worker-1")
        self.assertTrue(user.groups.filter(name="Night shift").exists())
