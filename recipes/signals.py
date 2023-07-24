from datetime import datetime

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from recipes.consumers import RealtimeConsumer

from recipes.models import (
    Ingredient,
    ProductListItem,
    ProductListWeek,
    Recipe,
    RecipeIngredient,
    RecipePlan,
    RecipePlanWeek,
)
from recipes.serializers import (
    IngredientSerializer,
    ProductListItemSerializer,
    RecipePlanSerializer,
    RecipePlanWeekSerializer,
    RecipeSerializer,
)
from recipes.services.measurings import amount_to_grams
from recipes.services.realtime import ModelInfo, register_models
from telegram_bot.services.notifications import send_notification

# from recipes.services.plans import update_plan_week

###


def get_current_plan_week():
    now = datetime.now()
    plan, _ = RecipePlanWeek.objects.get_or_create(year=now.year, week=now.isocalendar()[1])
    return plan


def get_product_list(year: int, week: int):
    product_week: ProductListWeek | None = ProductListWeek.objects.filter(year=year, week=week).first()
    return product_week


def unactual_product_list(year: int, week: int):
    product_week = get_product_list(year, week)
    if product_week and product_week.is_actual:
        product_week.is_actual = False
        product_week.save(update_fields=["is_actual"])


def unactual_plan_product_list(plan: RecipePlanWeek):
    unactual_product_list(plan.year, plan.week)


@receiver(pre_save, sender=RecipeIngredient)
def recipe_pre_save(sender: RecipeIngredient, instance, **kwargs):
    instance.amount_grams = amount_to_grams(instance.amount, instance.amount_type)


@receiver(pre_save, sender=ProductListWeek)
def product_list_week_changed(sender, instance, **kwargs):
    try:
        old = ProductListWeek.objects.get(pk=instance.pk)
    except ProductListWeek.DoesNotExist:
        old = instance

    if instance.is_filled and not old.is_filled:
        send_notification("products_filled", week=str(instance))


@receiver(pre_save, sender=RecipePlanWeek)
def plan_week_changed(sender, instance, **kwargs):
    try:
        old = RecipePlanWeek.objects.get(pk=instance.pk)
    except RecipePlanWeek.DoesNotExist:
        old = instance

    if instance.is_filled and not old.is_filled:
        send_notification("weekplan_ready", week=str(instance))


@receiver(pre_delete, sender=RecipePlan)
@receiver(pre_save, sender=RecipePlan)
def recipe_plan_changed(sender, instance: RecipePlan, **kwargs):
    unactual_product_list(instance.week.year, instance.week.week)


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
