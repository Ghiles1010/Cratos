"""
Auth views: login validation, session creation, and /me endpoint.
"""
import json

from django.contrib.auth.models import User
from django.test import Client, TestCase


class AuthViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user("alice", password="correct-password")

    def _post_login(self, body):
        return self.client.post(
            "/api/auth/login/",
            data=json.dumps(body),
            content_type="application/json",
        )

    def test_valid_credentials_return_user_data(self):
        resp = self._post_login({"username": "alice", "password": "correct-password"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["user"]["username"], "alice")

    def test_wrong_password_returns_401(self):
        resp = self._post_login({"username": "alice", "password": "wrong"})
        self.assertEqual(resp.status_code, 401)

    def test_missing_password_returns_400(self):
        resp = self._post_login({"username": "alice"})
        self.assertEqual(resp.status_code, 400)

    def test_me_authenticated_returns_profile(self):
        self.client.force_login(User.objects.get(username="alice"))
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "alice")
