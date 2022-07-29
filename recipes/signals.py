from datetime import datetime

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from recipes.models import Recipe, RecipeIngredient, RecipePlanWeek
from recipes.services.measurings import amount_to_grams
from recipes.services.plans import update_plan_week


def get_current_plan_week():
    now = datetime.now()
    plan, _ = RecipePlanWeek.objects.get_or_create(
        year=now.year, week=now.isocalendar()[1]
    )
    return plan


@receiver(pre_save, sender=RecipeIngredient)
def recipe_pre_save(sender: RecipeIngredient, instance, **kwargs):

    instance.amount_grams = amount_to_grams(instance.amount, instance.amount_type)


@receiver(post_save, sender=Recipe)
def recipe_post_save(sender: Recipe, instance, **kwargs):
    update_plan_week(get_current_plan_week())


@receiver(post_save, sender=RecipePlanWeek)
def recipe_plan_post_save(sender: RecipePlanWeek, instance, **kwargs):
    update_plan_week(get_current_plan_week())
