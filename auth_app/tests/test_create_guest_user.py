"""Tests for the create_guest_user management command."""

# 1. Standard library
from io import StringIO

# 2. Third-party
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

# 3. Local
from auth_app.management.commands.create_guest_user import (
    GUEST_EMAIL, GUEST_NAME, GUEST_PASSWORD)


class CreateGuestUserTests(TestCase):
    """Check that the guest user is created once and can log in."""

    def run_command(self):
        """Run the command and return its text output."""
        out = StringIO()
        call_command('create_guest_user', stdout=out)
        return out.getvalue()

    def test_command_creates_the_guest_user(self):
        """The guest user exists afterwards with the expected data."""
        self.run_command()
        user = User.objects.get(username=GUEST_EMAIL)
        self.assertEqual(user.email, GUEST_EMAIL)
        self.assertEqual(user.first_name, GUEST_NAME)
        self.assertTrue(user.check_password(GUEST_PASSWORD))

    def test_command_can_run_twice(self):
        """A second run does not create a second user."""
        self.run_command()
        output = self.run_command()
        self.assertEqual(User.objects.count(), 1)
        self.assertIn('already exists', output)
