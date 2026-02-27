"""
OriginChecker: allowlist enforcement, host normalisation, default port resolution.
"""
from django.test import TestCase

from webhooks.models import AllowedOrigin
from webhooks.services.errors import URLPolicyError
from webhooks.services.origin_checker import OriginChecker


class OriginCheckerTest(TestCase):

    def setUp(self):
        AllowedOrigin.objects.create(scheme="https", host="hooks.example.com", port=443)

    def test_listed_origin_passes(self):
        # Should not raise
        OriginChecker().check_url("https://hooks.example.com/events")

    def test_unlisted_origin_raises_policy_error(self):
        with self.assertRaises(URLPolicyError):
            OriginChecker().check_url("https://evil.com/steal")

    def test_default_http_port_resolved_to_80(self):
        AllowedOrigin.objects.create(scheme="http", host="internal.local", port=80)
        # URL omits port – checker must infer 80 and match the row
        OriginChecker().check_url("http://internal.local/hook")

    def test_non_http_scheme_raises_policy_error(self):
        with self.assertRaises(URLPolicyError):
            OriginChecker().check_url("ftp://hooks.example.com/upload")
