from django.core.management.base import BaseCommand, CommandError

from recipes.services.telegram import send_notification, send_notification_profile
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class Command(BaseCommand):
    help = "Send telegram notification"

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("--force", "-F", action="store_true", help="Force send notification to all profiles")
        parser.add_argument("--user", "-U", help="Send notification to one user")

    def handle(self, *args, **options):
        name = options["name"]
        user = options.get("user")
        if user:
            try:
                user_m = User.objects.get(Q(username=user) | Q(email=user))
            except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
                raise CommandError(f"User '{user}' does not exist") from e

            if not user_m.profile:
                raise CommandError("User hasn't profile yet")
            send_notification_profile(name, user_m.profile)

        else:
            send_notification(name, force=bool(options.get("force")))
