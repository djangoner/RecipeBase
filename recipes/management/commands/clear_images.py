from django.core.management.base import BaseCommand
from recipes.tasks import check_unused_images


class Command(BaseCommand):
    help = "Clear unused and empty images from DB"

    def handle(self, *args, **options):
        check_unused_images()
