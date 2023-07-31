from recipes.models import ProductListItem
from telegram_bot.services.modes.core import BaseChatMiddleware
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from telegram_bot.services.search import search_ingredient
from telebot.handler_backends import SkipHandler

from telegram_bot.services.utils import get_current_product_week


class ModeProductList(BaseChatMiddleware):
    def pre_process(self, message: Message, data):

        msg_text = message.text
        if not msg_text:
            return

        if msg_text.startswith("/"):
            return

        matches = search_ingredient(msg_text)

        if not matches:  # Matches not found
            self.instance.reply_to(message, "✅ Добавлено в список покупок")
            week = get_current_product_week()
            ProductListItem.objects.create(week=week, title=msg_text)
            return SkipHandler()

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

        self.instance.reply_to(message, "Возможно вы имели ввиду:", reply_markup=keyboard)
        return SkipHandler()
        # self.instance.send_message(message.chat.id, "")
