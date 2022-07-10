from django.db.models.signals import pre_save
from django.dispatch import receiver

from recipes.models import Recipe, RecipeIngredient
from recipes.services import amount_to_grams


@receiver(pre_save, sender=RecipeIngredient)
def recipe_pre_save(sender: RecipeIngredient, instance, **kwargs):

    instance.amount_grams = amount_to_grams(instance.amount, instance.amount_type)
