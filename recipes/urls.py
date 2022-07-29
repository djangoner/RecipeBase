"""RecipeBase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from rest_framework import routers

from recipes.views import (IngredientViewset, MealTimeViewset,
                           ProductListItemViewset, ProductListWeekViewset,
                           RecipeImageViewset, RecipeIngredientViewset,
                           RecipePlanViewset, RecipePlanWeekViewset,
                           RecipeRatingViewset, RecipeTagViewset,
                           RecipeViewset)

router = routers.DefaultRouter()
router.register("recipes", RecipeViewset)
router.register("recipe_images", RecipeImageViewset)
# router.register("recipe_ingredients", RecipeIngredientViewset)
router.register("recipe_tags", RecipeTagViewset)
router.register("ingredients", IngredientViewset)
router.register("meal_time", MealTimeViewset)
router.register("recipe_plan", RecipePlanViewset)
router.register("recipe_plan_week", RecipePlanWeekViewset)
router.register("recipe_rating", RecipeRatingViewset)
router.register("product_list_week", ProductListWeekViewset)
router.register("product_list_item", ProductListItemViewset)

urlpatterns = [
]
