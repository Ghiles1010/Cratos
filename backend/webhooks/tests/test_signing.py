"""
Webhook signing: HMAC-SHA256 header generation and verifiability.
"""
import hashlib
import hmac

from django.test import SimpleTestCase

from webhooks.services.signing import sign


class WebhookSigningTest(SimpleTestCase):

    def test_required_headers_are_present(self):
        headers = sign(b'{"event": "ping"}', "mysecret")
        self.assertIn("X-Cratos-Timestamp", headers)
        self.assertIn("X-Cratos-Signature", headers)

    def test_signature_format_is_sha256_prefixed(self):
        headers = sign(b"payload", "s3cr3t")
        self.assertTrue(headers["X-Cratos-Signature"].startswith("sha256="))

    def test_signature_is_independently_verifiable(self):
        payload = b'{"task_id": "abc"}'
        secret = "webhook-secret"
        headers = sign(payload, secret)

        timestamp = headers["X-Cratos-Timestamp"]
        signed_content = f"{timestamp}.".encode() + payload
        expected = "sha256=" + hmac.new(
            secret.encode(), signed_content, hashlib.sha256
        ).hexdigest()

        self.assertEqual(headers["X-Cratos-Signature"], expected)
