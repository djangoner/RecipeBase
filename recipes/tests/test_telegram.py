from django.test import TestCase
from recipes.models import RecipePlanWeek
from recipes.services import telegram


class TelegramTestCase(TestCase):
    def test_get_notifications_dict(self):
        d = telegram.get_notifications_dict()
        for k, v in d.items():
            assert isinstance(k, str)
            assert isinstance(v, str)

    def test_get_current_plan_week(self):
        assert isinstance(telegram.get_current_plan_week(), RecipePlanWeek)
