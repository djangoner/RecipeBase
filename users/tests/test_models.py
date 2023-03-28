from django.test import SimpleTestCase

from users.tests.factories import UserProfileFactory


class UsersTestCase(SimpleTestCase):
    def test_user_str(self):
        profile = UserProfileFactory.build()
        assert str(profile) == str(profile.user)
