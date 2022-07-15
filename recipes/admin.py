from django.contrib import admin

from recipes.models import (Ingredient, MealTime, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipePlanWeek,
                            RecipeTag)


class RecipeIngredientsInline(admin.StackedInline):
    extra = 0
    model = RecipeIngredient
    readonly_fields = ["amount_grams"]


class RecipeImageInline(admin.TabularInline):
    extra = 0
    model = RecipeImage

class RecipePlanInline(admin.TabularInline):
    extra = 0
    model = RecipePlan


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "short_description", "created", "edited"]
    search_fields = ["title", "content"]
    filter_horizontal = ("tags",)

    inlines = [RecipeIngredientsInline, RecipeImageInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient"]
    search_fields = ["recipe", "ingredient"]
    autocomplete_fields = ["recipe", "ingredient"]


@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ["image", "title"]
    search_fields = ["image", "title"]


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ("title", "recipes_count")
    search_fields = ("title",)


@admin.register(MealTime)
class MealTimeAdmin(admin.ModelAdmin):
    list_display = ["title", "time", "num", "is_primary"]

@admin.register(RecipePlanWeek)
class RecipePlanWeekAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "week")
    list_filter = ("year", "week")
    inlines = [RecipePlanInline]


@admin.register(RecipePlan)
class RecipePlanAdmin(admin.ModelAdmin):
    list_display = ["week", "meal_time"]
    list_filter = ["meal_time"]
    search_fields = ["week"]
