from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class TaskCategory(models.Model):

    title = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    sort = models.PositiveSmallIntegerField(_("Сортировка"), null=True, blank=True)
    author = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_("Автор"),
        related_name="task_categories",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(_("Время создания"), auto_now_add=True)

    class Meta:
        ordering = ["-sort", "title"]
        verbose_name = _("Категория задач")
        verbose_name_plural = _("Категории задач")

    def __str__(self) -> str:
        return self.title


class Task(models.Model):
    category = models.ForeignKey(TaskCategory, models.CASCADE, related_name="childrens", verbose_name=_("Категория"))
    icon = models.CharField(max_length=255, null=True, blank=True)

    is_completed = models.BooleanField(_("Завершен"), default=False)
    title = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), null=True, blank=True)
    priority = models.PositiveSmallIntegerField(
        _("Приоритет"),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    sort = models.PositiveSmallIntegerField(_("Сортировка"), null=True, blank=True)
    parent = models.ForeignKey("self", models.CASCADE, related_name="childrens", verbose_name=_("Родительская задача"), null=True, blank=True)
    deadline = models.DateTimeField(_("Дата задачи"), null=True, blank=True)

    author = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_("Автор"),
        related_name="task_author",
        null=True,
        blank=True,
    )
    assigned = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_("Ответственный"),
        related_name="task_assigned",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(_("Время создания"), auto_now_add=True)

    class Meta:
        ordering = ["deadline", "priority"]
        verbose_name = _("Задача")
        verbose_name_plural = _("Задачи")

    def __str__(self) -> str:
        return self.title
