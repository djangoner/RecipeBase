from django.shortcuts import render
from rest_framework import decorators, response, serializers, viewsets

from recipes.models import (Ingredient, MealTime, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipeTag)
from recipes.serializers import (IngredientSerializer, MealTimeSerializer,
                                 RecipeImageSerializer,
                                 RecipeIngredientSerializer,
                                 RecipePlanSerializer, RecipeSerializer,
                                 RecipeTagSerializer)
from recipes.services import MEASURING_CONVERT, MEASURING_TYPES


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
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

        measuring_types = [{"id": k, "title": v} for k,v in MEASURING_TYPES]

        return response.Response(
            {
                "types": measuring_types,
                "convert": MEASURING_CONVERT,
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


class RecipePlanViewset(viewsets.ModelViewSet):
    queryset = RecipePlan.objects.all()
    serializer_class = RecipePlanSerializer
