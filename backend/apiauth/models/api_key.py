import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone


class APIKey(models.Model):
    """Simple API key model for the standalone scheduler."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduler_api_key',
    )
    key = models.CharField(max_length=64, unique=True, db_index=True)
    label = models.CharField(max_length=128, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f'API Key for {self.user} ({self.label or "default"})'

    @classmethod
    def generate_key(cls) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(40))

    @classmethod
    def create_for_user(cls, user, label=''):
        return cls.objects.create(user=user, key=cls.generate_key(), label=label)

    def regenerate(self):
        self.key = self.generate_key()
        self.save(update_fields=['key'])
        return self.key

    def touch(self):
        """Update last_used timestamp."""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])
