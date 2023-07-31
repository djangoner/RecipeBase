from datetime import date, datetime
from typing import Optional
from recipes.models import ProductListItem, ProductListWeek, RecipePlan, RecipePlanWeek
from telegram_bot.models import TELEGRAM_NOTIFICATIONS_MANUAL, TelegramChat
from telegram_bot.services.telegram_handlers import get_bot

from telegram_bot.services.utils import (
    SITE_DOMAIN,
    WEEKDAYS_LONG_STR,
    WEEKDAYS_STR,
    get_current_plan_week,
    get_current_product_week,
    get_notifications_dict,
    get_plan_items_filtered,
    get_product_list_filtered,
    get_product_list_missed_filtered,
    get_product_list_on_week_filtered,
    get_recipe_flags,
    product_item_amount_str,
    render_product_item,
    telegram_log,
)
from users.models import UserProfile
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.contrib.auth.models import AbstractBaseUser

log = telegram_log.getChild("Notifications")
log.setLevel("DEBUG")


def render_plan_day(week_plan: RecipePlanWeek, plans: list[RecipePlan]):
    now = datetime.now()
    today_day = now.weekday() + 1

    text = ""
    i = 0

    if len(plans) < 1:  # No items
        return ""

    for plan in plans:
        if not plan.recipe:
            continue
        if i > 0:
            text += "\n\n"
        else:
            text += "\n"
        i += 1
        recipe_flags = get_recipe_flags(plan.recipe)
        recipe_flags_str = f"({', '.join([f.value for f in recipe_flags])})" if recipe_flags else ""

        text += f"<b>{plan.meal_time.title}</b>: {plan.recipe.title} <u><i>{recipe_flags_str}</i></u>"
        log.debug(f"WeekPlan: {week_plan}, today: {today_day}, {plan.pk}")

        comment = plan.recipe.comment
        if comment:
            comment = comment.replace("\n\n", "\n")
            text += f"\n<b>Комментарий:</b> <pre>{comment}</pre>"
    return text


def get_notification_text(name: str, **options) -> Optional[str]:
    now = datetime.now()
    today_day = now.weekday() + 1
    today_str = now.strftime("%d.%m.%Y")
    day = None
    day_offset = options.get("day_offset")
    week_str = options.get("week", "")
    if day_offset:
        day = today_day + day_offset

    if (name == "weekdays_morning" and today_day in [1, 2, 3, 4, 5]) or (name == "weekend_morning" and today_day) in [
        6,
        7,
    ]:
        if day_offset == 1:
            day_tx = "завтра"
        else:
            day_tx = "сегодня"
        text = f"<b>На {day_tx} в плане</b> ({today_str}):\n"
        week_plan = get_current_plan_week()
        plans = get_plan_items_filtered(week_plan, day=day)
        text += render_plan_day(week_plan, plans)

        if not plans:
            return
        return text
    elif name == "week_plan":
        week_plan = get_current_plan_week()
        text = ""
        for day, day_name in WEEKDAYS_LONG_STR.items():
            if day < 1:
                continue

            day_date = date.fromisocalendar(week_plan.year, week_plan.week, day)
            day_str = day_date.strftime("%d.%m")

            after = ""
            if day_date == now.date():
                after = "<u>(сегодня)</u>"

            text += f"<b>{day_str} {day_name} {after}</b>:\n"

            plans = get_plan_items_filtered(week_plan, day=day)
            plan_day = render_plan_day(week_plan, plans)
            if plan_day:
                text += plan_day + "\n\n"
            else:
                text += "- Нет планов\n\n"

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
            text += "\n\n<b>Также на неделе:</b>\n"

            for item in on_week:
                text += render_product_item(item)

        return text
    elif name == "products_missed":
        text = f"<b>Пропущенные продукты</b> ({today_str}):\n"
        week = get_current_product_week()
        product_items: list[ProductListItem] = get_product_list_missed_filtered(week)
        if len(product_items) < 1:  # No items
            return None
        for item in product_items:
            text += render_product_item(item)

        return text

    elif name == "product_list":
        week_plan = options.get("week_plan")
        if not week_plan:
            week_plan = get_current_product_week()
        date_start, date_end = week_plan.week_dates
        # fmt = '%m.%d'
        fmt = "%d.%m"
        text = f"<b>Список покупок ({date_start.strftime(fmt)}-{date_end.strftime(fmt)})</b>:\n\n"

        product_items: list[ProductListItem] = list(week_plan.items.all())  # type: ignore
        product_items.sort(key=lambda x: x.day if x.day is not None else 99)
        for item in product_items:
            if item.is_completed:
                continue
            # state_str = "+" if item.is_completed else "-"
            amounts_str = product_item_amount_str(item)
            day_str = WEEKDAYS_STR[item.day] if item.day is not None else "-"

            text += f"<pre>[{day_str:<2}] {item.title} {amounts_str}</pre>\n"

        return text

    elif name == "products_filled":
        return f"✅ Список покупок для {week_str} готов! Рекомендуется выполнить синхронизацию."

    elif name == "weekplan_ready":
        return f"✅ План на неделю {week_str} готов!"

    elif name == "notif_synced":
        return "Успешно выполнена фоновая синхронизация"

    return None


def get_notification_keyboard(name: str, **options):
    now = datetime.now()
    today_day = now.weekday() + 1
    day = None
    day_offset = options.get("day_offset")
    if day_offset:
        day = today_day + day_offset

    keyboard = InlineKeyboardMarkup()
    if name in ["weekdays_morning", "weekend_morning"]:
        plan = get_current_plan_week()
        url = SITE_DOMAIN + f"/week_plan?year={plan.year}&week={plan.week}"
        keyboard.add(InlineKeyboardButton("План на сегодня", url=url))

        items = get_plan_items_filtered(plan, day=day)
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


def send_notification_telegram_id(name: str, user_id: int, **text_kwargs):
    assert name in get_notifications_dict().keys(), "Invalid notification name"
    log.debug(f"Sending notification {name} for {user_id}")

    bot = get_bot()
    text = get_notification_text(name, **text_kwargs)
    keyboard = get_notification_keyboard(name, **text_kwargs)

    if not text:
        log.warning(f"Notitfication text empty for {user_id}")
        return False

    bot.send_message(user_id, text, reply_markup=keyboard)


def send_notification_profile(name: str, profile: UserProfile, **text_kwargs):
    assert name in get_notifications_dict().keys(), "Invalid notification name"
    log.debug(f"Sending notification {name} for {profile}")

    bot = get_bot()
    text = get_notification_text(name, **text_kwargs)
    keyboard = get_notification_keyboard(name)

    telegram_chat: TelegramChat = profile.telegram_chat
    user_id = telegram_chat.uid

    if not user_id:
        log.warning(f"Telegram ID not specified for {profile.user}")
        return
    elif not text:
        log.warning(f"Notitfication text empty for {profile.user}")
        return

    bot.send_message(user_id, text, reply_markup=keyboard)


def send_notification(name: str, force: bool = False, **text_kwargs):
    assert name in get_notifications_dict().keys(), "Invalid notification name"
    log.info(f"Sending notification: {name}")

    for profile in UserProfile.with_telegram().all():
        if not profile.telegram_chat:
            continue
        enabled_notifications = profile.telegram_chat.telegram_notifications
        notif_enabled = name in enabled_notifications or name in [n[0] for n in TELEGRAM_NOTIFICATIONS_MANUAL]
        log.debug(f"Checking profile: {profile} ({notif_enabled} - {','.join(enabled_notifications)})")

        if notif_enabled or force:
            send_notification_profile(name, profile, **text_kwargs)


def send_product_list(week: ProductListWeek, user: AbstractBaseUser):
    if not user.profile:  # type: ignore
        return

    send_notification_profile("product_list", user.profile, week_plan=week)  # type: ignore


def send_notif_synced(week: ProductListWeek, user: AbstractBaseUser):
    if not user.profile:  # type: ignore
        return

    send_notification_profile("notif_synced", user.profile, week_plan=week)  # type: ignore
