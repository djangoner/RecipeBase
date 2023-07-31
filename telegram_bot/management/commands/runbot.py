from django.core.management.base import BaseCommand

from telegram_bot.services.telegram_handlers import get_bot


class Command(BaseCommand):
    help = "Run telegram bot in polling mode"

    def handle(self, *args, **options):
        bot = get_bot()
        bot.polling(True, interval=2)
