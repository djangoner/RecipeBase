import uuid
from datetime import datetime

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from adminsortable.models import SortableMixin

from recipes.services.measurings import MEASURING_TYPES, short_text

# // Helpers
DESC_LENGTH = 80
User = get_user_model()


def gen_uuid() -> str:
    return str(uuid.uuid4())


def recipe_image_upload_to(instance: "RecipeImage", filename: str):
    ext = filename.split(".")[-1]
    uuid = gen_uuid()
    return f"uploads/recipe_images/{instance.recipe.pk}/{uuid}.{ext}"


def get_default_comments():
    return {i: "" for i in range(1, 7 + 1)}


# // Models \\


class Recipe(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    content = RichTextField(_("Содержание"), blank=True)
    content_source = RichTextField(_("Содержание (изначальное) "), blank=True)
    short_description = models.TextField(_("Короткое описание"), null=True, blank=True)
    comment = models.TextField(_("Комментарий"), null=True, blank=True)
    portion_count = models.FloatField(_("Кол-во порций"), null=True, blank=True)
    cooking_time = models.IntegerField(_("Примерное время приготовления"), null=True, blank=True)

    source_link = models.CharField(_("Источника"), max_length=255, blank=True, null=True)
    tags = models.ManyToManyField("RecipeTag", "recipes", verbose_name=_("Метки"), blank=True)

    created = models.DateTimeField(_("Создан"), auto_now_add=True, null=True)
    edited = models.DateTimeField(_("Изменен"), auto_now=True, null=True)
    author = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    is_archived = models.BooleanField(_("Архивирован"), default=False)

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_short_description(self, length=None):
        if length is None:
            length = DESC_LENGTH

        if self.short_description:
            return short_text(self.short_description, length)

        return short_text(strip_tags(self.content) or strip_tags(self.content_source), length)

    get_short_description.short_description = _("Краткое содержание")  # type: ignore


class RecipeImage(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        models.SET_NULL,
        related_name="images",
        verbose_name=_("Рецепт"),
        null=True,
        blank=False,
    )
    image = models.ImageField(_("Изображение"), upload_to=recipe_image_upload_to)
    title = models.CharField(_("Заголовок"), max_length=100, blank=True, null=True)
    num = models.SmallIntegerField(_("Сортировка"), null=True, blank=True)

    class Meta:
        ordering = ["num", "-id"]
        verbose_name = _("Изображение рецепта")
        verbose_name_plural = _("Изображения рецептов")

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f"#{self.id} {self.image}"


class Ingredient(models.Model):
    title = models.CharField(_("Название"), unique=True, max_length=100)
    description = models.TextField(_("Описание"), null=True, blank=True)
    category = models.ForeignKey(
        "IngredientCategory",
        models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name=_("Категория"),
        blank=True,
        null=True,
    )
    min_pack_size = models.SmallIntegerField(
        _("Объём упаковки"),
        null=True,
        blank=True,
        help_text=_("Минимальный размер упаковки в граммах / миллилитрах"),
    )
    item_weight = models.SmallIntegerField(
        _("Вес одной шт"),
        null=True,
        blank=True,
    )
    price = models.PositiveSmallIntegerField(_("Цена"), null=True, blank=True)
    need_buy = models.BooleanField(_("Требует покупки"), default=True)
    edible = models.BooleanField(_("Съедобный"), default=True)

    class Meta:
        ordering = ["title", "-id"]
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        models.CASCADE,
        related_name="ingredients",
        verbose_name=_("Рецепт"),
        blank=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name=_("Ингредиент"),
    )
    amount = models.FloatField(_("Количество"), max_length=15)
    amount_grams = models.SmallIntegerField(_("Количество в граммах"), editable=False, blank=True, null=True)
    amount_type = models.CharField(_("Единица измерения"), choices=MEASURING_TYPES, default="g", max_length=15)
    is_main = models.BooleanField(_("Основной игредиент"), default=False)

    class Meta:
        verbose_name = _("Ингредиент рецепта")
        verbose_name_plural = _("Ингредиенты рецептов")

    def __str__(self):
        return f"{self.recipe}: {self.ingredient}"


class RegularIngredient(models.Model):
    ingredient = models.OneToOneField(
        Ingredient,
        models.CASCADE,
        related_name="regular_ingredients",
        verbose_name=_("Ингредиент"),
    )
    day = models.PositiveSmallIntegerField(
        _("День недели"),
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    amount = models.FloatField(_("Количество"), max_length=15)
    amount_type = models.CharField(_("Единица измерения"), choices=MEASURING_TYPES, default="g", max_length=15)

    class Meta:
        verbose_name = _("Регулярный ингредиент")
        verbose_name_plural = _("Регулярные ингредиенты")

    def __str__(self):
        return f"{self.ingredient}"


class RecipeTag(models.Model):
    title = models.CharField(_("Название метки"), max_length=50)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Метка рецепта")
        verbose_name_plural = _("Метки рецептов")

    def __str__(self):
        return self.title

    def recipes_count(self):
        return self.recipes.count()

    recipes_count.verbose_name = _("Количество рецептов")  # type: ignore


class MealTime(models.Model):

    title = models.CharField(_("Название"), max_length=255)
    time = models.TimeField(_("Примерное время"), null=True, blank=True)
    num = models.SmallIntegerField(_("Сортировка"), null=True, blank=True)
    is_primary = models.BooleanField(
        _("Основной прием пищи"),
        help_text=_("Является ли прием пищи основным (обязательным на каждый день)"),
        default=False,
    )

    class Meta:
        ordering = [F("num").asc(nulls_last=True), F("time").asc(nulls_last=True)]
        verbose_name = _("Время приема пищи")
        verbose_name_plural = _("Время приема пищи")

    def __str__(self) -> str:
        if self.time:
            return f"{self.time} - {self.title}"
        else:
            return f"{self.title}"


class RecipeRating(models.Model):

    user = models.ForeignKey(User, models.CASCADE, related_name="ratings", verbose_name=_("Пользователь"))
    recipe = models.ForeignKey(
        Recipe,
        models.CASCADE,
        related_name="ratings",
        verbose_name=_("Рецепт"),
        blank=True,
    )
    rating = models.SmallIntegerField(_("Оценка"), validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        verbose_name = _("Оценка рецепта")
        verbose_name_plural = _("Оценка рецептов")
        # unique_together = [["user", "recipe"]]

    def __str__(self) -> str:
        return f"{self.recipe} {self.user} - {self.rating}"


class RecipePlanWeek(models.Model):
    year = models.SmallIntegerField(_("Год"))
    week = models.SmallIntegerField(_("Неделя"))

    comments = models.JSONField(_("Комментарии"), default=get_default_comments)

    class Meta:
        ordering = ["-year", "-week"]
        verbose_name = _("План недели")
        verbose_name_plural = _("Планы недели")

    def __str__(self) -> str:
        return f"{self.year}-{self.week}"


class RecipePlan(models.Model):

    week = models.ForeignKey(
        RecipePlanWeek,
        models.CASCADE,
        verbose_name=_("План недели"),
        blank=True,
        related_name="plans",
    )
    day = models.PositiveSmallIntegerField(
        _("День недели"),
        blank=False,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    date = models.DateField(_("Дата"), null=True, blank=True)

    meal_time = models.ForeignKey(MealTime, models.CASCADE, verbose_name=_("Время приема пищи"))
    recipe = models.ForeignKey(
        Recipe,
        models.SET_NULL,
        verbose_name=_("Рецепт"),
        null=True,
        blank=True,
        related_name="plans",
    )

    class Meta:
        ordering = ["day", "meal_time__num"]
        verbose_name = _("План рецепта")
        verbose_name_plural = _("План рецепта")

    def __str__(self) -> str:
        return f"{self.week}.{self.day} {self.meal_time}"

    def gen_date(self) -> datetime:
        date = datetime.strptime(" ".join(map(str, [self.week.year, self.week.week, self.day])), "%G %V %u")
        return date

    def check_date(self):
        date = self.gen_date()

        if not self.date or date != self.date:
            self.date = date
            self.save(update_fields=["date"])


class ProductListWeek(models.Model):
    year = models.SmallIntegerField(_("Год"))
    week = models.SmallIntegerField(_("Неделя"))

    class Meta:
        ordering = ["-year", "-week"]
        verbose_name = _("Список продуктов недели")
        verbose_name_plural = _("Списки продуктов недель")

    def __str__(self) -> str:
        return f"{self.year}-{self.week}"


class ProductListItem(models.Model):

    week = models.ForeignKey(
        ProductListWeek,
        models.CASCADE,
        verbose_name=_("Список продуктов недели"),
        blank=True,
        related_name="items",
    )
    day = models.PositiveSmallIntegerField(
        _("День недели"),
        blank=False,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
    )
    # recipe = models.ForeignKey(
    #     Recipe, models.SET_NULL, verbose_name=_("Рецепт"), null=True, blank=True
    # )
    ingredient = models.ForeignKey(
        Ingredient,
        models.CASCADE,
        related_name="plan_items",
        verbose_name=_("Ингредиент"),
        null=True,
        blank=True,
    )
    ingredients = models.ManyToManyField(
        RecipeIngredient,
        related_name="plan_items",
        verbose_name=_("Ингредиенты рецептов"),
        blank=True,
    )
    is_auto = models.BooleanField(_("Автоматический"), default=False)
    is_deleted = models.BooleanField(_("Удален"), default=False)
    ##

    is_completed = models.BooleanField(_("Завершен"), default=False)
    title = models.CharField(_("Название"), max_length=255)
    amount = models.FloatField(_("Количество"), null=True, blank=True, max_length=15)
    amount_type = models.CharField(
        _("Единица измерения"),
        choices=MEASURING_TYPES,
        default="g",
        max_length=15,
        null=True,
        blank=True,
    )

    description = models.TextField(_("Описание"), null=True, blank=True)
    priority = models.PositiveSmallIntegerField(
        _("Приоритет"),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    author = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_("Автор"),
        related_name="product_item_author",
        null=True,
        blank=True,
    )
    assigned = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_("Ответственный"),
        related_name="product_item_assigned",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(_("Время создания"), auto_now_add=True)
    # edited = models.DateTimeField(_("Время полследнего редактирования"), auto_now=True)
    ##

    class Meta:
        ordering = ["day", "priority"]
        verbose_name = _("Список покупок")
        verbose_name_plural = _("Список покупок")

    def __str__(self) -> str:
        return f"{self.week}.{self.day} {self.title}"


class Shop(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    category_sort = models.ManyToManyField("IngredientCategory", through="ShopIngredientCategory", blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")

    def __str__(self) -> str:
        return self.title


class IngredientCategory(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    icon = models.CharField(_("Иконка"), max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Категория ингредиента")
        verbose_name_plural = _("Категории ингредиентов")

    def __str__(self) -> str:
        return self.title


class ShopIngredientCategory(SortableMixin, models.Model):
    shop = models.ForeignKey(Shop, models.CASCADE, verbose_name=_("Магазин"))
    category = models.ForeignKey(
        IngredientCategory,
        models.CASCADE,
        related_name="sorting",
        verbose_name=_("Категория"),
    )
    num = models.SmallIntegerField(_("Сортировка"), null=True, blank=True)

    class Meta:
        # ordering = [F("num").asc(nulls_last=True)]
        ordering = ["num"]
        verbose_name = _("Магазин сортировка ингредианта")
        verbose_name_plural = _("Магазин сортировка ингредиента")
        unique_together = (("shop", "category"),)

    def __str__(self) -> str:
        # return self.shop.title + " - " + self.category.title'
        return f"#{self.num}"
