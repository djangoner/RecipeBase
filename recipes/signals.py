from datetime import datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver
from recipes.consumers import RealtimeConsumer

from recipes.models import Ingredient, ProductListItem, Recipe, RecipeIngredient, RecipePlan, RecipePlanWeek
from recipes.serializers import (
    IngredientSerializer,
    ProductListItemSerializer,
    RecipePlanSerializer,
    RecipePlanWeekSerializer,
    RecipeSerializer,
)
from recipes.services.measurings import amount_to_grams
from recipes.services.realtime import ModelInfo, register_models

# from recipes.services.plans import update_plan_week

###


def get_current_plan_week():
    now = datetime.now()
    plan, _ = RecipePlanWeek.objects.get_or_create(year=now.year, week=now.isocalendar()[1])
    return plan


@receiver(pre_save, sender=RecipeIngredient)
def recipe_pre_save(sender: RecipeIngredient, instance, **kwargs):
    instance.amount_grams = amount_to_grams(instance.amount, instance.amount_type)


register_models(
    [
        ModelInfo(ProductListItem, ProductListItemSerializer),
        ModelInfo(RecipePlan, RecipePlanSerializer),
        ModelInfo(RecipePlanWeek, RecipePlanWeekSerializer),
        ModelInfo(Ingredient, IngredientSerializer),
        ModelInfo(Recipe, RecipeSerializer),
    ],
    callback=RealtimeConsumer.send_raw_data,
)

# @receiver(post_save, sender=Recipe)
# def recipe_post_save(sender, instance: Recipe, **kwargs):
#     debounce_upd_plan_current_week()


# @receiver(post_save, sender=RecipePlan)
# def recipe_plan_post_save(sender, instance: RecipePlan, **kwargs):
#     instance.check_date()
#     debounce_upd_plan(instance.week)


# @receiver(post_save, sender=RecipePlanWeek)
# def recipe_plan_week_post_save(sender, instance: RecipePlanWeek, **kwargs):
#     debounce_upd_plan(instance)
