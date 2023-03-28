import logging
from telegram_bot.services.telegram_handlers import get_bot

bot = get_bot()
logging.info(f"Bot init: {bot}")
