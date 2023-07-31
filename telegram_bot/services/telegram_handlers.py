import logging
from functools import lru_cache

import telebot
from telebot.handler_backends import CancelUpdate, SkipHandler
from telebot.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from recipes.models import Ingredient, ProductListItem
from telegram_bot.models import ChatModeChoices
from telegram_bot.services.modes.core import BaseChatMiddleware
from telegram_bot.services.modes.product_list import ModeProductList
from telegram_bot.services.search import search_ingredient
from telegram_bot.services.utils import (
    BOT_TOKEN,
    get_current_product_week,
    parse_command,
)

log = logging.getLogger("TelegramHandlers")
telebot.apihelper.ENABLE_MIDDLEWARE = True


class Keyboards:
    @property
    def main(cls):
        k = ReplyKeyboardMarkup(resize_keyboard=True)
        k.add("План на неделю", "План на сегодня", "План на завтра")
        k.add("Список покупок", "Список на сегодня")

        return k


class OnlyUsersExistsMiddleware(BaseChatMiddleware):
    def __init__(self, *args, **kwargs) -> None:
        self.update_types = ["message"]

        super().__init__(*args, **kwargs)

    def pre_process(self, message: Message, data):
        chat = self.get_chat(message)

        if not chat or not chat.get_allowed():
            bot = get_bot()
            bot.reply_to(message, text="Access denied")
            return CancelUpdate()

    def post_process(self, message, data, exception):
        pass


class ChatModesMiddleware(BaseChatMiddleware):
    chat_modes: dict[str, BaseChatMiddleware] = {ChatModeChoices.PRODUCT_LIST: ModeProductList}

    def __init__(self, instance: telebot.TeleBot) -> None:
        self.update_types = ["message"]

        for mode in self.chat_modes:
            self.chat_modes[mode] = self.chat_modes[mode](instance)

        super().__init__(instance)

    def get_mode_cls(self, mode: str) -> BaseChatMiddleware | None:
        return self.chat_modes.get(mode)

    def pre_process(self, message: Message, data):
        chat = self.get_chat(message)
        if not chat or not chat.get_allowed():
            return
        ##
        msg_text = message.text

        if msg_text and msg_text.startswith("/chat_mode"):
            new_mode = msg_text.split(" ", 2)[-1].upper()
            if new_mode in self.chat_modes or new_mode == "CM":
                chat.chat_mode = new_mode
                chat.save(update_fields=["chat_mode"])
                self.instance.reply_to(message, f"Режим чата изменен на {chat.chat_mode}")
                return SkipHandler()
            else:
                self.instance.reply_to(message, f"Текущий режим: {chat.chat_mode}")
                return SkipHandler()
        ##
        mode_str = chat.chat_mode
        mode_cls = self.get_mode_cls(mode_str)
        if mode_cls:
            return mode_cls.pre_process(message, data)

    # def post_process(self, message, data, exception):
    #     super().post_process(message, data, exception)


def _get_bot():
    assert BOT_TOKEN is not None, "Bot token is empty"
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", use_class_middlewares=True)

    bot_info = bot.get_me()
    log.info(f"Bot run as @{bot_info.username}")
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

    bot.setup_middleware(OnlyUsersExistsMiddleware(bot))
    bot.setup_middleware(ChatModesMiddleware(bot))

    @bot.message_handler(commands=["start", "help", "menu"])
    def send_welcome(message: Message):
        tx = """
Бот базы рецептов. Примеры команд:

/list - список покупок
/list_today - список покупок на сегодня
/plan - план на неделю
/plan_day - план на сегодня
/plan_tomorrow - план на завтра

/list_add (ингредиент) - Добавить в список продуктов
"""
        reply_message(bot, message, tx, reply_markup=Keyboards().main)

    @bot.message_handler(commands=["product_list", "list"])
    @bot.message_handler(func=message_contains("Список покупок"))
    def notif_product_list_week(message: Message):
        r = send_notification_telegram_id("product_list", message.chat.id)
        if r is False:
            reply_message(bot, message, "Список покупок пуст")

    @bot.message_handler(commands=["list_today"])
    @bot.message_handler(func=message_contains("Список на сегодня"))
    def notif_product_list_today(message: Message):
        r = send_notification_telegram_id("products_reminder", message.chat.id)
        if r is False:
            reply_message(bot, message, "Список покупок пуст")

    @bot.message_handler(commands=["plan", "plan_week"])
    @bot.message_handler(func=message_contains("План на неделю"))
    def notif_plan_week(message: Message):
        r = send_notification_telegram_id("week_plan", message.chat.id)
        if r is False:
            reply_message(bot, message, "План пуст")

    @bot.message_handler(commands=["plan_day"])
    @bot.message_handler(func=message_contains(["План на день", "План на сегодня"]))
    def notif_plan_day(message: Message):
        r = send_notification_telegram_id("weekdays_morning", message.chat.id)
        if r is False:
            reply_message(bot, message, "На сегодня планов нет")

    @bot.message_handler(commands=["list_add"])
    def product_list_add(message: Message):
        if not message.text:
            return

        msg_text = message.text.split(" ", 2)[-1]

        if not msg_text:
            bot.reply_to(message, "Напишите название ингредиента после /list_add. Например: /list_add бананы")
            return

        matches = search_ingredient(msg_text)

        if not matches:  # Matches not found
            bot.reply_to(message, "✅ Добавлено в список покупок")
            week = get_current_product_week()
            ProductListItem.objects.create(week=week, title=msg_text)
            return

        ## Matches found

        keyboard = InlineKeyboardMarkup()
        for match in matches[:5]:
            keyboard.add(
                InlineKeyboardButton(text=match.ingredient.title, callback_data=f"add_ing:{match.ingredient.pk}")
            )

        keyboard.add(
            InlineKeyboardButton(text="-- Нет нужного варианта --", callback_data=f"add_ing_default:{msg_text}")
        )
        keyboard.add(InlineKeyboardButton(text="Отменить", callback_data="cancel"))

        bot.reply_to(message, "Возможно вы имели ввиду:", reply_markup=keyboard)
        # return SkipHandler()

    @bot.message_handler(commands=["plan_tomorrow"])
    @bot.message_handler(func=message_contains(["План на завтра"]))
    def notif_plan_tomorrow(message: Message):
        r = send_notification_telegram_id("weekdays_morning", message.chat.id, day_offset=1)
        if r is False:
            reply_message(bot, message, "На завтра планов нет")

    @bot.message_handler(func=lambda message: True)
    def unknown_command(message: Message):
        bot.reply_to(message, "Неизвестная команда. /help")

    @bot.callback_query_handler(func=lambda x: True)
    def callback_handler(cb: CallbackQuery):
        cmd, cmd_args = parse_command(cb.data)
        chat_id = cb.message.chat.id
        msg_id = cb.message.id

        if cmd == "cancel":
            bot.edit_message_text("Отменено", chat_id, msg_id)

        elif cmd == "add_ing":
            ing = Ingredient.objects.get(id=cmd_args[0])
            week = get_current_product_week()
            ProductListItem.objects.create(week=week, ingredient=ing, title=ing.title)

            bot.edit_message_text(f"✅ Добавлено в список покупок:\n\n<pre>{ing.title}</pre>", chat_id, msg_id)
        elif cmd == "add_ing_default":
            week = get_current_product_week()
            ProductListItem.objects.create(week=week, ingredient=ing, title=cmd_args[1])

            bot.edit_message_text("✅ Добавлено в список покупок", chat_id, msg_id)
