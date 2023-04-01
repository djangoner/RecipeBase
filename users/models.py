from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField


User = get_user_model()


TELEGRAM_NOTIFICATIONS = [
    ("weekdays_morning", "Будни утром"),
    ("weekend_morning", "Выходные утром"),
    ("products_reminder", "Купить продукты на завтра"),
    ("products_missed", "Пропущенные продукты"),
]

TELEGRAM_NOTIFICATIONS_MANUAL = [
    ("product_list", "Список продуктов"),
    ("week_plan", "План на неделю"),
    ("notif_synced", "Уведомление о синхронизации"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name="profile")
    icon = models.CharField(_("Иконка"), max_length=50, null=True, blank=True)
    show_rate = models.BooleanField(_("Показывать в рейтинге"), default=True)
    num = models.PositiveSmallIntegerField(_("Сортировка"), null=True, blank=True)

    conditions_include = models.BooleanField(_("Включить в условия недели"), default=False)

    telegram_id = models.CharField(_("ID аккаунта телеграмм"), max_length=20, null=True, blank=True)
    telegram_notifications = MultiSelectField(
        _("Telegram уведомления"), max_length=255, choices=TELEGRAM_NOTIFICATIONS, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профиль пользователя")
        ordering = [
            F("num").asc(nulls_last=True),
        ]

    def __str__(self) -> str:
        return self.user.__str__()
