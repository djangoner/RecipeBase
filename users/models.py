from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name="profile")
    icon = models.CharField(_("Иконка"), max_length=50, null=True, blank=True)
    show_rate = models.BooleanField(_("Показывать в рейтинге"), default=True)
    num = models.PositiveSmallIntegerField(_("Сортировка"), null=True, blank=True)

    conditions_include = models.BooleanField(_("Включить в условия недели"), default=False)

    telegram_chat = models.OneToOneField(
        "telegram_bot.TelegramChat", models.SET_NULL, null=True, blank=True, related_name="user_profile"
    )

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профиль пользователя")
        ordering = [
            F("num").asc(nulls_last=True),
        ]

    def __str__(self) -> str:
        return self.user.__str__()

    @classmethod
    def with_telegram(self):
        return self.objects.filter(telegram_chat__isnull=False)
