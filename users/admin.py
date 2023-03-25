from django.contrib import admin

from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "num", "show_rate", "conditions_include")
    search_fields = ("user",)
    list_editable = ["num", "show_rate", "conditions_include"]
