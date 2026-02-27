from django.core.exceptions import ValidationError
from django.db import models


class AllowedOrigin(models.Model):
    """
    Explicit allowlist for outbound webhook callbacks.

    A callback URL is permitted only if its normalized origin (scheme + host + port)
    matches one of these rows.

    Normalization rules:
      - scheme must be "http" or "https"
      - host is stored and compared lowercased, with any trailing dot stripped
      - if URL omits the port, it is treated as:
          http  -> 80
          https -> 443
      - if URL specifies a port (e.g. :8001), it must match exactly

    Examples:
      ("https", "hooks.stripe.com", 443)
      ("http",  "localhost",        8001)
      ("http",  "localhost",        80)   # allows http://localhost/ (implicit 80)
    """

    scheme = models.CharField(
        max_length=5,
        choices=[('http', 'http'), ('https', 'https')],
    )
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['scheme', 'host', 'port'],
                name='uniq_allowed_origin',
            )
        ]
        verbose_name = 'Allowed Origin'
        verbose_name_plural = 'Allowed Origins'

    def clean(self):
        self.host = (self.host or '').strip().lower().rstrip('.')
        if not self.host:
            raise ValidationError({'host': 'Host is required.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'
