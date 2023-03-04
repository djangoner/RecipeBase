import logging
import os
from datetime import datetime
from typing import Optional

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from recipes.models import ProductListItem, ProductListWeek, Recipe, RecipeIngredient, RecipePlan, RecipePlanWeek
from recipes.services.measurings import measuring_str
from users.models import TELEGRAM_NOTIFICATIONS, TELEGRAM_NOTIFICATIONS_MANUAL, UserProfile
from django.contrib.auth.models import User

BOT_TOKEN = os.getenv("BOT_TOKEN")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "")

log = logging.getLogger("Telegram")

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


def get_bot():
    assert BOT_TOKEN is not None, "Bot token is empty"
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
    return bot


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


def get_plan_items_filtered(week_plan: RecipePlanWeek) -> list[RecipePlan]:
    res = []
    plans: list[RecipePlan] = week_plan.plans.all()  # type: ignore
    for plan in plans:
        if not plan.recipe:
            continue
        if plan.day != get_today_day():
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
        if item.day:
            continue
        if item.is_completed:
            continue

        res.append(item)
    return res


def get_product_list_missed_filtered(week_plan: ProductListWeek) -> list[ProductListItem]:
    res = []
    items: list[ProductListItem] = week_plan.items.all()  # type: ignore
    for item in items:
        if not item.day or item.day < get_today_day():
            continue
        if item.is_completed:
            continue

        res.append(item)
    return res


def get_recipe_flags(recipe: Recipe):
    recipe_flags: list[str] = []
    if recipe.images.count() < 1:
        recipe_flags.append("нет фото")

    if recipe.ratings.count() < 3:
        recipe_flags.append("нет оценок")

    return recipe_flags


################################
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
    day_str = WEEKDAYS_STR[item.day] if item.day else "-"
    text = f"\n- [{day_str:<2}] {item.title} {product_item_amount_str(item)}"
    if item.ingredient and item.ingredient.description:
        text += f"\n<b>Комментарий:</b> <pre>{item.ingredient.description}</pre>"
    return text


################################


def get_notification_text(name: str, **options) -> Optional[str]:
    now = datetime.now()
    today_day = now.weekday() + 1
    today_str = now.strftime("%d.%m.%Y")

    if (name == "weekdays_morning" and today_day in [1, 2, 3, 4, 5]) or (name == "weekend_morning" and today_day) in [
        6,
        7,
    ]:
        text = f"<b>На сегодня в плане</b> ({today_str}):\n"
        week_plan = get_current_plan_week()
        plans = get_plan_items_filtered(week_plan)
        i = 0

        if len(plans) < 1:  # No items
            return None

        for plan in plans:
            if not plan.recipe:
                continue
            if i > 0:
                text += "\n\n"
            else:
                text += "\n"
            i += 1
            recipe_flags = get_recipe_flags(plan.recipe)
            recipe_flags_str = f"({', '.join(recipe_flags)})" if recipe_flags else ""

            text += f"<b>{plan.meal_time.title}</b>: {plan.recipe.title} <u><i>{recipe_flags_str}</i></u>"
            log.debug(f"WeekPlan: {week_plan}, today: {today_day}, {plan.pk}")

            if plan.recipe.comment:
                text += f"\n<b>Комментарий:</b> <pre>{plan.recipe.comment}</pre>"
        if i == 0:
            text += "Ничего нет"

        comments: dict[str, str]
        comments = week_plan.comments  # type: ignore
        comment_today = comments.get(str(today_day))
        log.debug(f"WeekPlan comments: {comments}")
        if comment_today:
            text += f"\n\n\n<b>Комментарий на день:</b>\n<pre>{comment_today}</pre>"

        return text
    elif name == "products_reminder":
        text = f"<b>Сегодня нужно купить</b> ({today_str}):\n"
        week = get_current_product_week()
        items: list[ProductListItem] = get_product_list_filtered(week)
        if len(items) < 1:  # No items
            return None
        for item in items:
            text += render_product_item(item)

        # Also on week
        on_week = get_product_list_on_week_filtered(week)
        if on_week:
            text += "\nТакже на неделе:\n"

            for item in on_week:
                text += render_product_item(item)

        return text
    elif name == "products_missed":
        text = f"<b>Пропущенные продукты</b> ({today_str}):\n"
        week = get_current_product_week()
        items: list[ProductListItem] = get_product_list_missed_filtered(week)
        if len(items) < 1:  # No items
            return None
        for item in items:
            text += render_product_item(item)

        return text

    elif name == "product_list":
        week_plan = options.get("week_plan")
        if not week_plan:
            week_plan = get_current_product_week()
        date_start, date_end = week_plan.week_dates
        # fmt = '%m.%d'
        fmt = "%d.%m"
        text = f"<b>Список продуктов ({date_start.strftime(fmt)}-{date_end.strftime(fmt)})</b>:\n\n"

        items: list[ProductListItem] = list(week_plan.items.all())  # type: ignore
        items.sort(key=lambda x: x.day if x.day is not None else 99)
        for item in items:
            state_str = "+" if item.is_completed else "-"
            amounts_str = product_item_amount_str(item)
            day_str = WEEKDAYS_STR[item.day] if item.day is not None else "-"

            text += f"<pre>[{state_str}] [{day_str:<2}] {item.title} {amounts_str}</pre>\n"

        return text

    return None


def get_notification_keyboard(name: str):
    keyboard = InlineKeyboardMarkup()
    if name in ["weekdays_morning", "weekend_morning"]:
        plan = get_current_plan_week()
        url = SITE_DOMAIN + f"/week_plan?year={plan.year}&week={plan.week}"
        keyboard.add(InlineKeyboardButton("План на сегодня", url=url))

        items = get_plan_items_filtered(plan)
        btns = []
        for item in items:
            if not item.recipe:
                continue
            url = SITE_DOMAIN + f"/recipes/{item.recipe.pk}"
            btns.append(InlineKeyboardButton(item.recipe.title, url=url))
        keyboard.add(*btns, row_width=2)
    elif name == "products_reminder":
        plan = get_current_product_week()
        url = SITE_DOMAIN + f"/product_list?year={plan.year}&week={plan.week}"
        keyboard.add(InlineKeyboardButton("План на сегодня", url=url))

    return keyboard


def send_notification_profile(name: str, profile: UserProfile, **text_kwargs):
    assert name in get_notifications_dict().keys(), "Invalid notification name"
    log.debug(f"Sending notification {name} for {profile}")

    bot = get_bot()
    text = get_notification_text(name, **text_kwargs)
    keyboard = get_notification_keyboard(name)
    user_id = profile.telegram_id

    if not user_id:
        log.warning(f"Telegram ID not specified for {profile.user}")
        return
    elif not text:
        log.warning(f"Notitfication text empty for {profile.user}")
        return

    bot.send_message(user_id, text, reply_markup=keyboard)


def send_notification(name: str, force: bool = False):
    assert name in get_notifications_dict().keys(), "Invalid notification name"
    log.info(f"Sending notification: {name}")

    for profile in UserProfile.objects.all():
        log.debug(f"Checking profile: {profile}")

        if name in profile.telegram_notifications or force:
            send_notification_profile(name, profile)


def send_product_list(week: ProductListWeek, user: User):
    if not user.profile:
        return

    send_notification_profile("product_list", user.profile, week_plan=week)
