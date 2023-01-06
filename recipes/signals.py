from datetime import datetime
from time import time

from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from recipes.models import Recipe, RecipeIngredient, RecipePlan, RecipePlanWeek
from recipes.services.measurings import amount_to_grams
from recipes.services.plans import update_plan_week


def get_current_time_milli():
    return int(round(time() * 1000))


def debouncer(callback, throttle=1000):

    last_millis = get_current_time_milli()

    def throttle_f(*args, **kwargs):
        nonlocal last_millis
        curr_millis = get_current_time_milli()
        if (curr_millis - last_millis) > throttle:
            last_millis = get_current_time_milli()
            callback(*args, **kwargs)

    return throttle_f


def update_plan_week_current():
    return update_plan_week(get_current_plan_week())


###

debounce_upd_plan_current_week = debouncer(update_plan_week_current, throttle=2000)
debounce_upd_plan = debouncer(update_plan_week, throttle=2000)


def get_current_plan_week():
    now = datetime.now()
    plan, _ = RecipePlanWeek.objects.get_or_create(year=now.year, week=now.isocalendar()[1])
    return plan


@receiver(pre_save, sender=RecipeIngredient)
def recipe_pre_save(sender: RecipeIngredient, instance, **kwargs):

    instance.amount_grams = amount_to_grams(instance.amount, instance.amount_type)


@receiver(post_save, sender=Recipe)
def recipe_post_save(sender, instance: Recipe, **kwargs):
    debounce_upd_plan_current_week()


@receiver(post_save, sender=RecipePlan)
def recipe_plan_post_save(sender, instance: RecipePlan, **kwargs):
    instance.check_date()
    debounce_upd_plan(instance.week)


@receiver(post_save, sender=RecipePlanWeek)
def recipe_plan_week_post_save(sender, instance: RecipePlanWeek, **kwargs):
    debounce_upd_plan(instance)
