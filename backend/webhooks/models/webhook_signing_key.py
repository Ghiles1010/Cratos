import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone


class WebhookSigningKey(models.Model):
    """Per-user HMAC signing secret for webhook payloads."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhook_signing_key',
    )
    secret = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_rotated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Webhook Signing Key'
        verbose_name_plural = 'Webhook Signing Keys'

    def __str__(self):
        return f'Webhook Signing Key for {self.user}'

    @classmethod
    def generate_secret(cls) -> str:
        alphabet = string.ascii_letters + string.digits
        suffix = ''.join(secrets.choice(alphabet) for _ in range(40))
        return f'whsec_{suffix}'

    def rotate(self):
        self.secret = self.generate_secret()
        self.last_rotated_at = timezone.now()
        self.save(update_fields=['secret', 'last_rotated_at'])
        return self.secret
