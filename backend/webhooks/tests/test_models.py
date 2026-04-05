from django.contrib.auth.models import User
from django.test import TestCase

from webhooks.models import WebhookSigningKey


class WebhookSigningKeyTest(TestCase):
    def test_generate_secret_has_whsec_prefix(self):
        user = User.objects.create_user("carol", password="pass")
        obj = WebhookSigningKey.objects.create(
            user=user,
            secret=WebhookSigningKey.generate_secret(),
        )
        self.assertTrue(obj.secret.startswith("whsec_"))
