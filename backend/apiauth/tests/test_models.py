from django.contrib.auth.models import User
from django.test import TestCase

from apiauth.models import APIKey


class APIKeyTest(TestCase):
    def test_create_for_user_generates_40_char_key(self):
        user = User.objects.create_user("alice", password="pass")
        api_key = APIKey.create_for_user(user)
        self.assertEqual(len(api_key.key), 40)
