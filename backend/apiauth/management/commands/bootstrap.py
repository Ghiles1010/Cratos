"""
Idempotent bootstrap command – runs automatically on every container start via entrypoint.sh.

Creates (if not already present):
  - Superuser  (CRATOS_ADMIN_USERNAME / CRATOS_ADMIN_PASSWORD)
  - API key    (auto-generated, printed to logs on first boot)
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Bootstrap Cratos: superuser and API key (idempotent)"

    def handle(self, *args, **options):
        user = self._ensure_superuser()
        self._ensure_api_key(user)

    def _ensure_superuser(self):
        username = os.environ.get("CRATOS_ADMIN_USERNAME", "admin")
        password = os.environ.get("CRATOS_ADMIN_PASSWORD", "admin")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"[bootstrap] Created admin user: {username}"))
        else:
            self.stdout.write(f"[bootstrap] Admin user already exists: {username}")
        return user

    def _ensure_api_key(self, user):
        from apiauth.models import APIKey

        _, created = APIKey.objects.get_or_create(
            user=user,
            defaults={'key': APIKey.generate_key(), 'label': 'default'},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("[bootstrap] API key created"))
        else:
            self.stdout.write("[bootstrap] API key already exists")

