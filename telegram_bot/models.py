from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from users.models import UserProfile


TELEGRAM_NOTIFICATIONS = [
    ("weekdays_morning", "Будни утром"),
    ("weekend_morning", "Выходные утром"),
    ("products_reminder", "Купить продукты на завтра"),
    ("products_missed", "Пропущенные продукты"),
    ("weekplan_ready", "План на неделю готов"),
    ("products_filled", "Список покупок готов"),
]

TELEGRAM_NOTIFICATIONS_MANUAL = [
    ("product_list", "Список покупок"),
    ("week_plan", "План на неделю"),
    ("notif_synced", "Уведомление о синхронизации"),
]


class ChatModeChoices(models.TextChoices):
    # Default mode
    COMMANDS = "CM", _("Команды")
    # Add all messages to product list
    PRODUCT_LIST = "PL", _("Список продуктов")


class TelegramChat(models.Model):
    uid = models.IntegerField(_("ID пользователя"), editable=False)
    username = models.CharField(_("Ник пользователя"), max_length=255, editable=False)
    first_name = models.CharField(_("Имя пользователя"), max_length=255, null=True, blank=True, editable=False)

    chat_mode = models.CharField(
        _("Режим работы"), max_length=2, choices=ChatModeChoices.choices, default=ChatModeChoices.COMMANDS
    )
    telegram_notifications = MultiSelectField(
        _("Telegram уведомления"), max_length=255, choices=TELEGRAM_NOTIFICATIONS, null=True, blank=True
    )
    allowed = models.BooleanField(
        _("Разрешить доступ"), default=False, help_text="Разрешить доступ к использованию бота"
    )

    created = models.DateTimeField(_("Дата создания"), auto_now_add=True, null=True)
    edited = models.DateTimeField(_("Дата редактирования"), auto_now=True, null=True)

    user_profile: "UserProfile"

    class Meta:
        verbose_name = _("Телеграм чат")
        verbose_name_plural = _("Телеграм чаты")

    def __str__(self):
        return self.username or str(self.uid)

    def get_allowed(self):
        return self.allowed
