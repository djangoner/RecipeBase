from datetime import datetime
from enum import Enum
import logging
import os
from typing import Optional
from recipes.models import ProductListItem, ProductListWeek, Recipe, RecipeIngredient, RecipePlan, RecipePlanWeek
from recipes.services.measurings import measuring_str
from recipes.services.plans import get_ingredient_packs
from telegram_bot.models import TELEGRAM_NOTIFICATIONS, TELEGRAM_NOTIFICATIONS_MANUAL

telegram_log = logging.getLogger("Telegram")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "")
BOT_TOKEN = os.getenv("BOT_TOKEN")
assert BOT_TOKEN is not None, "Bot token is empty"


WEEKDAYS_STR = {
    0: "Прошл",
    1: "Пн",
    2: "Вт",
    3: "Ср",
    4: "Чт",
    5: "Пт",
    6: "Сб",
    7: "Вс",
}

WEEKDAYS_LONG_STR = {
    0: "Прошлый",
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


class RecipeFlags(Enum):
    no_images = "нет фото"
    no_ratings = "нет оценок"


def get_today_day():
    now = datetime.now()
    today_day = now.weekday() + 1
    return today_day


def get_notifications_dict():
    return {**dict(TELEGRAM_NOTIFICATIONS), **dict(TELEGRAM_NOTIFICATIONS_MANUAL)}


def get_current_plan_week():
    now = datetime.now()
    plan, _ = RecipePlanWeek.objects.get_or_create(year=now.year, week=now.isocalendar()[1])
    return plan


def get_current_product_week():
    now = datetime.now()
    plan, _ = ProductListWeek.objects.get_or_create(year=now.year, week=now.isocalendar()[1])
    return plan


def product_item_amount_str(item: ProductListItem):
    amounts_str = ""
    if item.amount_type and item.amount:
        amounts_str = f"({int(item.amount)} {measuring_str(item.amount_type)})"
    else:
        amount_l = []
        ing: RecipeIngredient
        for ing in item.ingredients.all():
            amount_l.append(f"{int(ing.amount)} {measuring_str(ing.amount_type)}")

        if amount_l:
            amounts_str = "(" + ", ".join(amount_l) + ")"

    return amounts_str


def render_product_item(item: ProductListItem) -> str:
    if not item.ingredient:
        return ""
    day_str = WEEKDAYS_STR[item.day] if item.day else "-"
    packs = get_ingredient_packs(item)

    packs_pref = "кг" if item.ingredient.min_pack_size == 1000 else "шт"
    item_packs_str = f"<u>~{packs} {packs_pref}</u>" if packs else ""

    text = f"\n- [{day_str:<2}] {item.title} {item_packs_str} {product_item_amount_str(item)}"
    if item.ingredient and item.ingredient.description:
        text += f"\n<b>Комментарий:</b> <pre>{item.ingredient.description}</pre>"
    return text


def get_plan_items_filtered(week_plan: RecipePlanWeek, day: Optional[int] = None) -> list[RecipePlan]:
    if not day:
        day = get_today_day()

    res = []
    plans: list[RecipePlan] = week_plan.plans.all()  # type: ignore
    for plan in plans:
        if not plan.recipe:
            continue
        if plan.day != day:
            continue
        res.append(plan)
    return res


def get_product_list_filtered(week_plan: ProductListWeek) -> list[ProductListItem]:
    res = []
    items: list[ProductListItem] = week_plan.items.all()  # type: ignore
    for item in items:
        if not item.day or item.day != get_today_day():
            continue
        if item.is_completed:
            continue

        res.append(item)
    return res


def get_product_list_on_week_filtered(week_plan: ProductListWeek) -> list[ProductListItem]:
    res = []
    items: list[ProductListItem] = week_plan.items.all()  # type: ignore
    for item in items:
        if item.day and item.day < get_today_day() + 1:
            continue
        if item.is_completed:
            continue

        res.append(item)
    return res


def get_product_list_missed_filtered(week_plan: ProductListWeek) -> list[ProductListItem]:
    res = []
    items: list[ProductListItem] = week_plan.items.all()  # type: ignore
    for item in items:
        if not item.day or item.day > get_today_day():
            continue
        if item.is_completed:
            continue

        res.append(item)
    return res


def get_recipe_flags(recipe: Recipe):
    recipe_flags: list[RecipeFlags] = []
    if recipe.images.count() < 1:
        recipe_flags.append(RecipeFlags.no_images)

    if recipe.ratings.count() < 3:
        recipe_flags.append(RecipeFlags.no_ratings)

    return recipe_flags


def parse_command(command: str):
    spl = command.split(":")

    command = spl[0]
    arguments = spl[1:]

    return command, arguments


def command_name(command: str):
    return command.split(":", 2)[0]
