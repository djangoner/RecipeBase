from django.contrib import admin
from django.db.models import Count, F

from recipes.models import (
    Ingredient,
    IngredientCategory,
    MealTime,
    ProductListItem,
    ProductListWeek,
    Recipe,
    RecipeImage,
    RecipeIngredient,
    RecipeIngredientRecommendation,
    RecipePlan,
    RecipePlanWeek,
    RecipeRating,
    RecipeTag,
    RegularIngredient,
    Shop,
    ShopIngredientCategory,
    WeekPlanCondition,
)
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline
from simple_history.admin import SimpleHistoryAdmin
from djangoql.admin import DjangoQLSearchMixin


class RecipeIngredientsInline(admin.StackedInline):
    extra = 0
    model = RecipeIngredient
    readonly_fields = ["amount_grams", "ingredient"]


class RecipeImageInline(admin.TabularInline):
    extra = 0
    model = RecipeImage


class RecipePlanInline(admin.TabularInline):
    extra = 0
    model = RecipePlan
    autocomplete_fields = ["recipe", "meal_time"]


class RecipeRatingInline(admin.TabularInline):
    extra = 0
    model = RecipeRating
    autocomplete_fields = ["recipe", "user"]


class RecipeIngredientRecommendationInline(admin.TabularInline):
    extra = 0
    model = RecipeIngredientRecommendation
    autocomplete_fields = ["recipe", "ingredient"]


class ShopIngredientCategoryInline(SortableTabularInline):
    extra = 0
    model = ShopIngredientCategory
    readonly_fields = ["num"]
    # autocomplete_fields = ["shop", "category"]


class WeekPlanConditionInline(admin.StackedInline):
    extra = 0
    model = WeekPlanCondition


@admin.register(Recipe)
class RecipeAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin):
    list_display = ["title", "created", "edited", "get_cooked_times"]
    search_fields = ["title", "content"]
    filter_horizontal = ("tags", "recommendations_recipes", "recommendations_tags")

    inlines = [RecipeIngredientsInline, RecipeImageInline, RecipeIngredientRecommendationInline, RecipeRatingInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(cooked_times=Count(F("plans__date")))

    def get_cooked_times(self, obj):
        return getattr(obj, "cooked_times", None)

    get_cooked_times.short_description = "Приготовлений"  # type: ignore


@admin.register(Ingredient)
class IngredientAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin):
    list_display = ["title", "category", "min_pack_size", "price", "edible", "need_buy"]
    list_filter = ["need_buy", "edible", "category"]
    autocomplete_fields = ["category"]
    search_fields = ["title"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin):
    list_display = ["recipe", "ingredient"]
    search_fields = ["recipe__title", "ingredient__title"]
    autocomplete_fields = ["recipe", "ingredient"]


@admin.register(RegularIngredient)
class RegularIngredientAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin):
    list_display = ["ingredient", "amount", "amount_type", "active"]
    search_fields = ["ingredient__title"]
    list_editable = ["amount", "amount_type", "active"]
    autocomplete_fields = ["ingredient"]


@admin.register(RecipeImage)
class RecipeImageAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["id", "image", "title", "recipe_id", "created"]
    list_filter = ["created"]
    search_fields = ["image", "title"]


@admin.register(RecipeTag)
class RecipeTagAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("title", "recipes_count")
    search_fields = ("title",)


@admin.register(MealTime)
class MealTimeAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["title", "time", "num", "is_primary"]
    search_fields = ["title", "time"]
    list_editable = ["num"]


@admin.register(RecipePlanWeek)
class RecipePlanWeekAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("id", "year", "week")
    list_filter = ("year", "week")
    inlines = [RecipePlanInline]


@admin.register(RecipePlan)
class RecipePlanAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["week", "meal_time", "recipe"]
    list_filter = ["meal_time", "week__year", "week__week"]
    search_fields = ["week__year", "week__week", "recipe__title"]


@admin.register(ProductListWeek)
class ProductListWeekAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("id", "year", "week")
    list_filter = ("year", "week")
    search_fields = ["year", "week"]


@admin.register(ProductListItem)
class ProductListItemAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin):
    list_display = [
        "week",
        "title",
        "amount",
        "amount_type",
        "priority",
        "is_deleted",
        "is_auto",
    ]
    list_filter = [
        "is_auto",
        "is_deleted",
        "priority",
        "author",
        "assigned",
        "week__year",
        "week__week",
    ]
    search_fields = ["week__year", "week__week", "title", "description"]
    autocomplete_fields = ("author", "assigned", "week", "ingredient")
    filter_horizontal = ("ingredients",)


@admin.register(Shop)
class ShopAdmin(DjangoQLSearchMixin, NonSortableParentAdmin, admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ["title"]
    inlines = [ShopIngredientCategoryInline]


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("id", "title", "icon")
    search_fields = ["title"]


@admin.register(WeekPlanCondition)
class WeekPlanConditionAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "parent",
        "plan_field",
        "condition",
        "comparison_mode",
        "selector_type",
        "selector_value",
        "icon",
        "priority",
        "active",
    ]
    list_filter = ("condition", "comparison_mode", "plan_field")
    search_fields = ["title", "selector_type", "selector_value", "comparison_mode"]
    inlines = [WeekPlanConditionInline]
