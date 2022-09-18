import logging
from datetime import datetime

from django.db.models import Count, F, Func, Max, Prefetch, Q, Value
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import (decorators, exceptions, response, serializers,
                            viewsets)

from recipes.models import (Ingredient, MealTime, ProductListItem,
                            ProductListWeek, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipePlanWeek,
                            RecipeRating, RecipeTag)
from recipes.serializers import (IngredientSerializer, MealTimeSerializer,
                                 ProductListItemSerializer,
                                 ProductListWeekSerializer,
                                 ProductListWeekShortSerializer,
                                 RecipeImageSerializer,
                                 RecipeIngredientSerializer,
                                 RecipePlanSerializer,
                                 RecipePlanWeekSerializer,
                                 RecipePlanWeekShortSerializer,
                                 RecipeRatingSerializer, RecipeSerializer,
                                 RecipeTagSerializer)
from recipes.services.measurings import (MEASURING_CONVERT, MEASURING_SHORT,
                                         MEASURING_TYPES)
from recipes.services.plans import update_plan_week


class RecipeFilterSet(filters.FilterSet):
    rating = filters.CharFilter(method="filter_rating", label="Rating filter")
    compilation = filters.CharFilter(
        method="filter_compilation", label="Compilation filter"
    )
    tags_include = filters.ModelMultipleChoiceFilter(
        method="filter_tags_include", label="Tags include", queryset=RecipeTag.objects
    )
    tags_exclude = filters.ModelMultipleChoiceFilter(
        method="filter_tags_exclude", label="Tags exclude", queryset=RecipeTag.objects
    )
    cooking_time_gt = filters.NumberFilter("cooking_time", lookup_expr="gte")
    cooking_time_lt = filters.NumberFilter("cooking_time", lookup_expr="lte")

    class Meta:
        model = Recipe
        exclude = ("tags",)

    def filter_rating(self, queryset, name, value):
        for subval in value.split(","):
            queryset = self._filter_rating(queryset, name, subval)
        return queryset.distinct()

    def _filter_rating(self, queryset, name, value):
        if not len(value.split("_")) == 2:
            return queryset

        user, rating = value.split("_")
        rating_mode = None

        if rating.startswith("-"):
            rating_mode = False
            rating = rating[1:]
        elif rating.startswith("+"):
            rating_mode = True
            rating = rating[1:]

        rating = int(rating)
        user = int(user)

        q = [Q(ratings__user=user)]

        if rating_mode == True:
            q.append(Q(ratings__rating__gte=rating))
        elif rating_mode == False:
            q.append(Q(ratings__rating__lte=rating))
        else:
            q.append(Q(ratings__rating=rating))

        return queryset.filter(*q)

    def filter_tags_include(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(tags__in=value).distinct()

    def filter_tags_exclude(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.exclude(tags__in=value).distinct()

    def filter_compilation(self, queryset, name, value):
        if value != "archive":
            queryset = queryset.filter(is_archived=False)

        if value == "archive":
            qs = queryset.filter(is_archived=True)
            return qs
        elif value == "long_uncooked":
            qs = queryset.filter(
                last_cooked__lt=timezone.now() - timezone.timedelta(weeks=4)
            )
            return qs
        elif value == "vlong_uncooked":
            qs = queryset.filter(
                last_cooked__lt=timezone.now() - timezone.timedelta(weeks=8)
            )
            return qs
        elif value == "top10":
            qs = queryset.order_by("-cooked_times").filter(cooked_times__gt=0)
            return qs
        elif value == "new":
            week_firstday = timezone.now().today()
            while week_firstday.weekday() > 0:
                week_firstday = week_firstday - timezone.timedelta(days=1)
            qs = queryset.filter(Q(last_cooked=None) | (Q(last_cooked__gt=week_firstday.date()) & Q(cooked_times=1)))
            return qs
        else:
            logging.warning(f"Unknown compilation: '{value}'")

        return queryset


class RecipeViewset(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.prefetch_related(
            "author",
            "ratings",
            "ratings__user",
            "ingredients",
            "ingredients__ingredient",
            "tags",
            "images",
        )
        .annotate(cooked_times=Count(F("plans__date")))
        .annotate(last_cooked=Max(F("plans__date")))
        .distinct()
    )
    serializer_class = RecipeSerializer
    search_fields = ["title", "short_description", "comment"]
    filterset_class = RecipeFilterSet
    ordering_fields = [
        "created",
        "edited",
        "id",
        "title",
        "portion_count",
        "cooking_time",
        "last_cooked",
    ]

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
    search_fields = ["year", "week"]

    def get_serializer_class(self):
        short = self.request.GET.get("short")

        if short:
            return RecipePlanWeekShortSerializer

        return self.serializer_class

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

    def get_serializer_class(self):
        short = self.request.GET.get("short")

        if short:
            return ProductListWeekShortSerializer

        return self.serializer_class

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

    @decorators.action(["POST"], detail=True)
    def move_week(self, request, pk=None):
        week_plan, _ = ProductListItem.objects.get_or_create(pk=pk)
        week = get_object_or_404(ProductListWeek, pk=request.GET.get("week"))
        week_plan.week = week
        week_plan.save(update_fields=["week"])

        return self.retrieve(request)
