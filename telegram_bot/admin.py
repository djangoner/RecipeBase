from django.contrib import admin

from telegram_bot.models import TelegramChat


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_display = ("uid", "username", "first_name", "allowed", "edited")
    list_filter = ("allowed",)
    search_fields = ("username", "first_name", "id")
    readonly_fields = ("uid", "username", "first_name", "created", "edited")
