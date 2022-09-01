from datetime import datetime

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from rest_framework import (decorators, exceptions, response, serializers,
                            viewsets)

from recipes.models import (Ingredient, MealTime, ProductListItem,
                            ProductListWeek, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipePlanWeek,
                            RecipeRating, RecipeTag)
from recipes.serializers import (IngredientSerializer, MealTimeSerializer,
                                 ProductListItemSerializer,
                                 ProductListWeekSerializer,
                                 RecipeImageSerializer,
                                 RecipeIngredientSerializer,
                                 RecipePlanSerializer,
                                 RecipePlanWeekSerializer,
                                 RecipeRatingSerializer, RecipeSerializer,
                                 RecipeTagSerializer)
from recipes.services.measurings import (MEASURING_CONVERT, MEASURING_SHORT,
                                         MEASURING_TYPES)
from recipes.services.plans import update_plan_week


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        "author",
        "ratings",
        "ratings__user",
        "ingredients",
        "ingredients__ingredient",
        "tags",
        "images",
    )
    serializer_class = RecipeSerializer
    search_fields = ["title", "content", "content_source", "short_description"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeImageViewset(viewsets.ModelViewSet):
    queryset = RecipeImage.objects.all()
    serializer_class = RecipeImageSerializer


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    @decorators.action(["GET"], detail=False)
    def amount_types(self, request):

        measuring_types = [{"id": k, "title": v} for k, v in MEASURING_TYPES]

        return response.Response(
            {
                "types": measuring_types,
                "convert": MEASURING_CONVERT,
                "short": MEASURING_SHORT,
            }
        )


class RecipeIngredientViewset(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer


class RecipeTagViewset(viewsets.ModelViewSet):
    queryset = RecipeTag.objects.all()
    serializer_class = RecipeTagSerializer


class MealTimeViewset(viewsets.ModelViewSet):
    queryset = MealTime.objects.all()
    serializer_class = MealTimeSerializer


class RecipePlanWeekViewset(viewsets.ModelViewSet):
    queryset = RecipePlanWeek.objects.prefetch_related(
        "plans",
        "plans__meal_time",
        "plans__recipe",
        "plans__recipe__author",
        "plans__recipe__ratings",
        "plans__recipe__ratings__user",
        "plans__recipe__ingredients",
        "plans__recipe__ingredients__ingredient",
        "plans__recipe__tags",
        "plans__recipe__images",
    )
    serializer_class = RecipePlanWeekSerializer

    def get_object(self):
        pk = self.kwargs.get("pk", None)
        year, week = None, None
        if pk in ["current", "now"]:
            year, week = datetime.now().year, datetime.now().isocalendar()[1]
        elif pk:
            try:
                year, week = pk.split("_")
            except ValueError:
                pass

        if year or week:
            plan_week, _ = self.queryset.get_or_create(year=year, week=week)
            return plan_week

        return super().get_object()


class RecipePlanViewset(viewsets.ModelViewSet):
    queryset = RecipePlan.objects.prefetch_related(
        "meal_time",
        "recipe",
        "recipe__author",
        "recipe__ratings",
        "recipe__ratings__user",
        "recipe__ingredients",
        "recipe__ingredients__ingredient",
        "recipe__tags",
        "recipe__images",
    )
    serializer_class = RecipePlanSerializer


class RecipeRatingViewset(viewsets.ModelViewSet):
    queryset = RecipeRating.objects.prefetch_related("user")
    serializer_class = RecipeRatingSerializer


class ProductListWeekViewset(viewsets.ModelViewSet):
    queryset = ProductListWeek.objects.prefetch_related(
        "items",
        "items__ingredients",
        "items__ingredients__ingredient",
        "items__ingredients__recipe",
        "items__ingredients__recipe__ingredients",
        "items__ingredients__recipe__ingredients__ingredient",
        "items__ingredients__recipe__tags",
        "items__ingredients__recipe__images",
    )
    serializer_class = ProductListWeekSerializer

    def get_object(self):
        pk = self.kwargs.get("pk", None)
        year, week = None, None
        if pk in ["current", "now"]:
            year, week = datetime.now().year, datetime.now().isocalendar()[1]
        elif pk:
            try:
                year, week = pk.split("_")
            except ValueError:
                pass

        if year or week:
            plan_week, _ = ProductListWeek.objects.get_or_create(year=year, week=week)
            return plan_week

        return super().get_object()

    @decorators.action(["GET"], detail=True)
    def generate(self, request, pk=None):
        week = self.get_object()
        week_plan, _ = RecipePlanWeek.objects.get_or_create(
            year=week.year, week=week.week
        )
        update_plan_week(week_plan)

        return self.retrieve(request)


class ProductListItemViewset(viewsets.ModelViewSet):
    queryset = ProductListItem.objects.prefetch_related(
        "ingredients",
        "ingredients__ingredient",
        "ingredients__recipe",
        "ingredients__recipe__ingredients",
        "ingredients__recipe__ingredients__ingredient",
        "ingredients__recipe__tags",
        "ingredients__recipe__images",
    )
    serializer_class = ProductListItemSerializer
    filterset_fields = ["is_auto", "is_deleted", "is_completed"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
