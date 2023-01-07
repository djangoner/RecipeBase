from django.test import TestCase
from django.contrib.auth.models import User
import logging

from users.tests.factories import TokenFactory, UserFactory

logging.disable(logging.CRITICAL)


class UserViewsTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(self) -> None:
        self.user = User.objects.create(username="testuser", is_superuser=True)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_current_user(self):
        resp = self.client.get("/api/v1/users/current_user_info/")
        assert resp.status_code == 200
        resp_json = resp.json()

        assert resp_json["id"] == self.user.id
        assert resp_json["username"] == self.user.username

    def test_user_token_login(self):
        self.client.logout()
        user: User = UserFactory.create()

        resp = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": user.username,
                "password": "test123",
            },
        )
        assert resp.status_code == 200
        resp_json = resp.json()

        token = TokenFactory(user=user)
        assert resp_json["token"] == token.key
