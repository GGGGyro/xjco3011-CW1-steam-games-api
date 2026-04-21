"""
Django management command to create the default superuser account.

Runs idempotently: if a user with the target username already exists the
command exits silently, making it safe to include in every deploy pipeline.

Usage:
    python manage.py create_superuser
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

USERNAME = "YYDS"
EMAIL = "admin@example.com"
PASSWORD = "ZZZHR123"


class Command(BaseCommand):
    help = "Create the default superuser account if it does not already exist."

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.filter(username=USERNAME).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Superuser '{USERNAME}' already exists — skipping creation."
                )
            )
            return

        try:
            User.objects.create_superuser(
                username=USERNAME,
                email=EMAIL,
                password=PASSWORD,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser '{USERNAME}' created successfully."
                )
            )
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to create superuser '{USERNAME}': {exc}"
                )
            )
