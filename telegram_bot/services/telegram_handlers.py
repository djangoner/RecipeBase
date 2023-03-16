from functools import lru_cache
import logging
import telebot
from telebot.types import ReplyKeyboardMarkup, Message
from telebot.handler_backends import BaseMiddleware
from telegram_bot.services.utils import BOT_TOKEN

from users.models import UserProfile
from telebot.handler_backends import CancelUpdate


log = logging.getLogger("TelegramHandlers")
telebot.apihelper.ENABLE_MIDDLEWARE = True


class Keyboards:
    @property
    def main(cls):
        k = ReplyKeyboardMarkup(resize_keyboard=True)
        k.add("План на неделю", "План на сегодня", "План на завтра")
        k.add("Список продуктов", "Список на сегодня")

        return k


@lru_cache(10)
def profile_telegram_id_exists(uid: int) -> UserProfile | None:
    return UserProfile.objects.filter(telegram_id=uid).first()


class OnlyUsersExistsMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.update_types = ["message"]

    def pre_process(self, message: Message, data):
        profile = profile_telegram_id_exists(message.from_user.id)

        if not profile:
            bot = get_bot()
            bot.reply_to(message, text="Access denied")
            return CancelUpdate()

    def post_process(self, message, data, exception):
        pass


def _get_bot():
    assert BOT_TOKEN is not None, "Bot token is empty"
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", use_class_middlewares=True)
    log.info(f"Bot init: {bot}")
    if not isinstance(bot, str):
        register_bot_handlers(bot)
    return bot


@lru_cache(maxsize=1)
def get_bot():
    return _get_bot()


def reply_message(bot: telebot.TeleBot, message: Message, *args, **kwargs):
    """Reply to message sender"""
    return bot.send_message(message.chat.id, *args, **kwargs)


def message_contains(text: str | list[str]):
    """Telegram message contains"""

    def inner(message: Message) -> bool:

        text_list = [text] if isinstance(text, str) else text
        for t in text_list:
            if message.text and message.text.lower() == t.lower():
                return True

        return False

    return inner


def register_bot_handlers(bot: telebot.TeleBot):
    from telegram_bot.services.notifications import send_notification_telegram_id

    bot.setup_middleware(OnlyUsersExistsMiddleware())

    @bot.message_handler(commands=["start", "help", "menu"])
    def send_welcome(message: Message):
        tx = """
Бот базы рецептов. Примеры команд:

/list - список продуктов
/list_today - список продуктов на сегодня
/plan - план на неделю
/plan_day - план на сегодня
/plan_tomorrow - план на завтра
"""
        reply_message(bot, message, tx, reply_markup=Keyboards().main)

    @bot.message_handler(commands=["product_list", "list"])
    @bot.message_handler(func=message_contains("Список продуктов"))
    def notif_product_list_week(message: Message):
        r = send_notification_telegram_id("product_list", message.from_user.id)
        if r is False:
            reply_message(bot, message, "Список продуктов пуст")

    @bot.message_handler(commands=["list_today"])
    @bot.message_handler(func=message_contains("Список на сегодня"))
    def notif_product_list_today(message: Message):
        r = send_notification_telegram_id("products_reminder", message.from_user.id)
        if r is False:
            reply_message(bot, message, "Список продуктов пуст")

    @bot.message_handler(commands=["plan", "plan_week"])
    @bot.message_handler(func=message_contains("План на неделю"))
    def notif_plan_week(message: Message):
        r = send_notification_telegram_id("week_plan", message.from_user.id)
        if r is False:
            reply_message(bot, message, "План пуст")

    @bot.message_handler(commands=["plan_day"])
    @bot.message_handler(func=message_contains(["План на день", "План на сегодня"]))
    def notif_plan_day(message: Message):
        r = send_notification_telegram_id("weekdays_morning", message.from_user.id)
        if r is False:
            reply_message(bot, message, "На сегодня планов нет")

    @bot.message_handler(commands=["plan_tomorrow"])
    @bot.message_handler(func=message_contains(["План на завтра"]))
    def notif_plan_tomorrow(message: Message):
        r = send_notification_telegram_id("weekdays_morning", message.from_user.id, day_offset=1)
        if r is False:
            reply_message(bot, message, "На завтра планов нет")

    @bot.message_handler(func=lambda message: True)
    def unknown_command(message: Message):
        bot.reply_to(message, "Неизвестная команда. /help")
