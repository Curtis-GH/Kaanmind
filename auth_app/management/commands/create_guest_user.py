"""Management command that creates the guest user of the frontend.

The frontend offers a guest login with fixed credentials (see
``shared/js/config.js`` of the frontend). This command creates that user.
Run it once after the first migration:

    python manage.py create_guest_user
"""

# 1. Third-party
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

GUEST_EMAIL = 'kevin@kovacsi.de'
GUEST_PASSWORD = 'asdasdasd'
GUEST_NAME = 'Guest User'


class Command(BaseCommand):
    """Create the guest user if it does not exist yet."""

    help = 'Create the guest user used by the frontend guest login.'

    def handle(self, *args, **options):
        """Create the guest user. Running it twice changes nothing."""
        if User.objects.filter(username=GUEST_EMAIL).exists():
            self.stdout.write('Guest user already exists.')
            return
        User.objects.create_user(
            username=GUEST_EMAIL, email=GUEST_EMAIL,
            password=GUEST_PASSWORD, first_name=GUEST_NAME)
        self.stdout.write(self.style.SUCCESS('Guest user created.'))
