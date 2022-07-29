from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = "users"
    verbose_name = _("Авторизация")

    def ready(self):
        from . import signals  # NOQA
