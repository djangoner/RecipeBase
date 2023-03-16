import json

from django.http import HttpResponse

from telegram_bot.services.telegram_handlers import get_bot
from django.http.request import HttpRequest
import telebot
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def bot_view(request: HttpRequest):
    bot = get_bot()
    update = json.loads(request.body)

    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])

    return HttpResponse("ok")
