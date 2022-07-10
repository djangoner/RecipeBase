from django.contrib import admin

from recipes.models import (Ingredient, MealTime, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipeTag)


class RecipeIngredientsInline(admin.StackedInline):
    extra = 0
    model = RecipeIngredient
    readonly_fields = ['amount_grams']

class RecipeImageInline(admin.TabularInline):
    extra = 0
    model = RecipeImage

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'short_description', 'created', 'edited']
    search_fields = ['title', 'content']
    filter_horizontal = ('tags',)

    inlines = [RecipeIngredientsInline, RecipeImageInline]

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient']
    search_fields = ['recipe', 'ingredient']
    autocomplete_fields = ['recipe', 'ingredient']

@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'title']
    search_fields = ['image', 'title']

@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipes_count')
    search_fields = ('title',)

@admin.register(MealTime)
class MealTimeAdmin(admin.ModelAdmin):
    list_display = ['title', 'time', 'num']

@admin.register(RecipePlan)
class MealTimeAdmin(admin.ModelAdmin):
    list_display = ['year', 'week', 'meal_time']
    list_filter = ['year', 'week', 'meal_time']
