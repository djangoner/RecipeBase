from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name="profile")
    icon = models.CharField(_("Иконка"), max_length=50, null=True, blank=True)
    show_rate = models.BooleanField(_("Показывать в рейтинге"), default=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профиль пользователя")


    def __str__(self) -> str:
        return self.user.__str__()
