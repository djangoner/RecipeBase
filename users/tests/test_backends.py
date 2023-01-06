import logging
from django.test import TestCase
import pytest
from users.backends import CustomAuthorizationBackend

from users.tests.factories import UserFactory
from django.http.request import HttpRequest


logging.disable(logging.CRITICAL)


@pytest.fixture()
def request_fixture():
    return HttpRequest()


class UserBackendsTestCase(TestCase):
    def test_login_username(self):
        user = UserFactory()
        back = CustomAuthorizationBackend()

        res = back.authenticate(request_fixture, user.username, "test123")
        assert res == user

    def test_login_username_invalid_pass(self):
        user = UserFactory()
        back = CustomAuthorizationBackend()

        res = back.authenticate(request_fixture, user.username, "invalid_password")
        assert res is None

    def test_login_email(self):
        user = UserFactory()
        back = CustomAuthorizationBackend()

        res = back.authenticate(request_fixture, user.email, "test123")
        assert res == user

    def test_login_inactive(self):
        user = UserFactory(is_active=False)
        back = CustomAuthorizationBackend()

        res = back.authenticate(request_fixture, user.email, "test123")
        assert res is None

    def test_login_invalid(self):
        user = UserFactory()
        back = CustomAuthorizationBackend()

        res = back.authenticate(request_fixture, "invalid", "invalid")
        assert res is None
