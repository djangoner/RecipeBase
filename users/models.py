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

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профиль пользователя")
        ordering = [
            F("num").asc(nulls_last=True),
        ]

    def __str__(self) -> str:
        return self.user.__str__()
