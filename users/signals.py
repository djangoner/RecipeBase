from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender: User, instance, created, **kwargs):

    try:
        profile = instance.profile
    except ObjectDoesNotExist:
        profile = None

    if not profile:
        UserProfile.objects.create(user=instance)
