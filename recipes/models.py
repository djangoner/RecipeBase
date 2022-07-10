import uuid

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields import related
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from recipes.services import MEASURING_CONVERT, MEASURING_TYPES, short_text

# // Helpers
DESC_LENGTH = 80
User = get_user_model()

def recipe_image_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    uid = uuid.uuid4()
    return f"uploads/recipe_images/{instance.recipe.pk}/{uid}.{ext}"

# // Models \\


class Recipe(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    content = RichTextField(_("Содержание"), blank=True)
    content_source = RichTextField(_("Содержание (изначальное) "), blank=True)
    short_description = models.TextField(_("Короткое описание"), null=True, blank=True)

    source_link = models.URLField(
        _("Адрес источника"), max_length=255, blank=True, null=True)
    tags = models.ManyToManyField('RecipeTag', 'recipes', verbose_name=_("Метки"), blank=True)

    created = models.DateTimeField(_("Создан"), auto_now_add=True, null=True)
    edited = models.DateTimeField(_("Изменен"), auto_now=True, null=True)
    author = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_short_description(self, length=None):
        if length is None:
            length = DESC_LENGTH

        if self.short_description:
            return short_text(self.short_description, length)

        return short_text(strip_tags(self.content), length)

    get_short_description.short_description = _("Краткое содержание")


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, models.SET_NULL, related_name="images", verbose_name=_(
        "Рецепт"), null=True, blank=False)
    image = models.ImageField(
        _("Изображение"), upload_to=recipe_image_upload_to)
    title = models.CharField(
        _("Заголовок"), max_length=100, blank=True, null=True)
    num = models.SmallIntegerField(_("Сортировка"), null=True, blank=True)

    class Meta:
        ordering = ['num', '-id']
        verbose_name = _("Изображение рецепта")
        verbose_name_plural = _("Изображения рецептов")

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f"#{self.id} {self.image}"

class Ingredient(models.Model):
    title = models.CharField(_("Название"), max_length=100)

    class Meta:
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, models.CASCADE, related_name="ingredients", verbose_name=_("Рецепт"), blank=True)
    ingredient = models.ForeignKey(
        Ingredient, models.CASCADE, related_name="recipe_ingredients", verbose_name=_("Ингредиент"))
    amount = models.FloatField(_("Количество"), max_length=15)
    amount_grams = models.SmallIntegerField(_("Количество в граммах"), editable=False, blank=True, null=True)
    amount_type = models.CharField(
        _("Единица измерения"), choices=MEASURING_TYPES, default="g", max_length=15)

    class Meta:
        verbose_name = _("Ингредиент рецепта")
        verbose_name_plural = _("Ингредиенты рецептов")

    def __str__(self):
        return f"{self.recipe}: {self.ingredient}"

class RecipeTag(models.Model):
    title = models.CharField(_("Название метки"), max_length=50)

    class Meta:
        verbose_name = _("Метка рецепта")
        verbose_name_plural = _("Метки рецептов")

    def __str__(self):
        return self.title

    def recipes_count(self):
        return self.recipes.count()
    recipes_count.verbose_name = _("Количество рецептов")

class MealTime(models.Model):

    title = models.CharField(_("Название"), max_length=255)
    time = models.TimeField(_("Примерное время"))
    num = models.SmallIntegerField(_("Сортировка"), null=True, blank=True)

    class Meta:
        ordering = ["-num", "time"]
        verbose_name = _("Время приема пищи")
        verbose_name_plural = _("Время приема пищи")

    def __str__(self) -> str:
        return f"{self.time} - {self.title}"


class RecipePlan(models.Model):

    year = models.SmallIntegerField(_("Год"))
    week = models.SmallIntegerField(_("Неделя"))

    meal_time = models.ForeignKey(MealTime, models.CASCADE, verbose_name=_("Время приема пищи"))
    recipe = models.ForeignKey(Recipe, models.SET_NULL, verbose_name=_("Рецепт"), null=True, blank=True)

    class Meta:
        verbose_name = _("Запланированный рецепт")
        verbose_name_plural = _("Запланированные рецепты")

    def __str__(self) -> str:
        return f"{self.year}.{self.week} {self.meal_time}"
