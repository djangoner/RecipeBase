from django.contrib import admin

from tasks.models import Task, TaskCategory


class TasksInline(admin.StackedInline):
    model = Task
    extra = 0
    classes = ("collapse",)


@admin.register(TaskCategory)
class TaskGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "icon")
    search_fields = ("title",)
    inlines = [TasksInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "deadline", "created")
    list_filter = ("author", "priority")
    inlines = [TasksInline]
    autocomplete_fields = ["category"]
