from cachetools.func import ttl_cache
from telebot.handler_backends import BaseMiddleware
from telebot.types import Message, CallbackQuery
from telebot import TeleBot

from telegram_bot.models import TelegramChat


class BaseChatMiddleware(BaseMiddleware):
    instance: TeleBot

    def __init__(self, instance: TeleBot):
        self.instance = instance
        super().__init__()

    @classmethod
    @ttl_cache(10, 5)
    def _get_chat_by_id(
        cls, uid: int, username: str = "", first_name: str = "", auto_create: bool = True
    ) -> TelegramChat | None:
        """Get telegram chat model by user id"""
        if not auto_create:
            return TelegramChat.objects.filter(uid=uid).first()

        chat, _ = TelegramChat.objects.update_or_create(
            uid=uid, defaults={"username": username or "", "first_name": first_name or ""}
        )
        return chat

    @classmethod
    def get_chat(cls, message: Message, **opts):
        return cls._get_chat_by_id(
            uid=message.chat.id,
            username=message.chat.username,
            first_name=message.chat.first_name or message.chat.title,
            **opts
        )

    @classmethod
    def get_chat_callback(cls, cb: CallbackQuery, **opts):
        return cls._get_chat_by_id(
            uid=cb.message.chat.id,
            username=cb.message.chat.username,
            first_name=cb.message.chat.first_name or cb.message.chat.title,
            **opts
        )

    def pre_process(self, message: Message, data):
        pass

    def post_process(self, message: Message, data, exception: Exception):
        pass
