from django.core.management.base import BaseCommand
from telegram_bot.services.telegram_handlers import get_bot

from telegram_bot.services.utils import SITE_DOMAIN


class Command(BaseCommand):
    help = "Set telegram bot webhook"

    def add_arguments(self, parser):
        parser.add_argument("--domain", "-D", help="Webhook domain")
        parser.add_argument("--url", "-U", help="Webhook URL")
        parser.add_argument("--clear", "-C", action="store_true", help="Clear webhook")

    def handle(self, *args, **options):
        if options.get("clear"):
            bot = get_bot()
            r = bot.remove_webhook()
            print("Webhook removed: ", r)
            return

        domain = SITE_DOMAIN
        options_domain = options.get("domain")
        if options_domain:
            domain = options_domain

        url = "/webhooks/telegram_bot"
        options_url = options.get("url")
        if options_url:
            url = options_url

        assert domain is not None, "Empty domain"
        assert url is not None, "Empty url"

        abs_url = domain + url
        bot = get_bot()
        r = bot.set_webhook(abs_url)

        if r:
            print(f"\nWebhook successfully updated to: {abs_url}")
        else:
            print(f"\nFailed updating webhook to: {abs_url}")
