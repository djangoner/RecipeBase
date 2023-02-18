from django.core.management.base import BaseCommand

from recipes.services.telegram import send_notification


class Command(BaseCommand):
    help = "Send telegram notification"

    def add_arguments(self, parser):
        parser.add_argument("name")

    def handle(self, *args, **options):
        name = options["name"]
        send_notification(name)
