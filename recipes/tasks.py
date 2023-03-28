import logging
from recipes.models import RecipeImage
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

log = logging.getLogger("Tasks")


def check_unused_images():
    time_from = timezone.now() - timedelta(seconds=10)
    unused_images = RecipeImage.objects.filter(created__lt=time_from, recipe__isnull=True)

    logging.info(f"Clearing unused images: {unused_images.count()}. Deleting from: {time_from}")
    unused_images.delete()

    empty_images = RecipeImage.objects.filter(Q(image__isnull=True) | Q(image=""), created__lt=time_from)
    logging.info(f"Clearing empty images: {empty_images.count()}")
    empty_images.delete()
