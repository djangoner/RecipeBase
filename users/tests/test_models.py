


from django.test import TestCase

from users.tests.factories import UserProfileFactory


class UsersTestCase(TestCase):
    def test_user_str(self):
        profile = UserProfileFactory()
        assert str(profile) == str(profile.user)