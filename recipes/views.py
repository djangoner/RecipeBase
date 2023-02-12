import logging
from datetime import datetime

from django.db.models import Count, F, Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import (
    decorators,
    response,
    viewsets,
    permissions,
)

from recipes.models import (
    Ingredient,
    MealTime,
    ProductListItem,
    ProductListWeek,
    Recipe,
    RecipeImage,
    RecipeIngredient,
    RecipePlan,
    RecipePlanWeek,
    RecipeRating,
    RecipeTag,
    IngredientCategory,
    RegularIngredient,
    Shop,
)
from tasks.models import Task
from recipes.serializers import (
    IngredientReadSerializer,
    IngredientSerializer,
    MealTimeSerializer,
    ProductListItemReadSerializer,
    ProductListItemSerializer,
    ProductListWeekReadSerializer,
    ProductListWeekSerializer,
    ProductListWeekShortSerializer,
    RecipeImageSerializer,
    RecipeIngredientSerializer,
    RecipePlanReadSerializer,
    RecipePlanSerializer,
    RecipePlanWeekReadSerializer,
    RecipePlanWeekSerializer,
    RecipePlanWeekShortSerializer,
    RecipeRatingSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeTagSerializer,
    IngredientCategorySerializer,
    RegularIngredientSerializer,
    ShopSerializer,
)
from recipes.services.measurings import (
    MEASURING_CONVERT,
    MEASURING_SHORT,
    MEASURING_TYPES,
)
from recipes.services.plans import update_plan_week
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import fields


class RecipeFilterSet(filters.FilterSet):
    rating = filters.CharFilter(method="filter_rating", label="Rating filter")
    compilation = filters.CharFilter(method="filter_compilation", label="Compilation filter")
    tags_include = filters.CharFilter(
        method="filter_tags_include", label="Tags include"  # , queryset=RecipeTag.objects
    )
    tags_exclude = filters.CharFilter(
        method="filter_tags_exclude", label="Tags exclude"  # , queryset=RecipeTag.objects
    )
    ingredients_include = filters.CharFilter(
        method="filter_ingredients_include",
        label="Ingredients include",
        # queryset=Ingredient.objects,
    )
    ingredients_exclude = filters.CharFilter(
        method="filter_ingredients_exclude",
        label="Ingredients exclude",
        # queryset=Ingredient.objects,
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

        if rating_mode is True:
            q.append(Q(ratings__rating__gte=rating))
        elif rating_mode is False:
            q.append(Q(ratings__rating__lte=rating))
        else:
            q.append(Q(ratings__rating=rating))

        return queryset.filter(*q)

    def filter_tags_include(self, queryset, name, value: str):
        if not value:
            return queryset
        print(value)
        return queryset.filter(tags__in=value.split(",")).distinct()

    def filter_tags_exclude(self, queryset, name, value: str):
        if not value:
            return queryset
        return queryset.exclude(tags__in=value.split(",")).distinct()

    def filter_ingredients_include(self, queryset, name, value: str):
        if not value:
            return queryset
        return queryset.filter(ingredients__ingredient__in=value.split(",")).distinct()

    def filter_ingredients_exclude(self, queryset, name, value: str):
        if not value:
            return queryset
        return queryset.exclude(ingredients__ingredient__in=value.split(",")).distinct()

    def filter_compilation(self, queryset, name, value):
        if value != "archive":
            queryset = queryset.filter(is_archived=False)

        if value == "archive":
            qs = queryset.filter(is_archived=True)
            return qs
        elif value == "long_uncooked":
            qs = queryset.filter(
                last_cooked__lt=timezone.now() - timezone.timedelta(weeks=4),
                last_cooked__gt=timezone.now() - timezone.timedelta(weeks=8),
            )
            return qs
        elif value == "vlong_uncooked":
            qs = queryset.filter(last_cooked__lt=timezone.now() - timezone.timedelta(weeks=8))
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


@extend_schema_view(
    retrieve=extend_schema(responses=RecipeReadSerializer),
    create=extend_schema(responses=RecipeReadSerializer),
    list=extend_schema(responses=RecipeReadSerializer),
    update=extend_schema(responses=RecipeReadSerializer),
    patch=extend_schema(responses=RecipeReadSerializer),
)
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
        .order_by(*Recipe._meta.ordering or [])
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


@extend_schema_view(
    retrieve=extend_schema(responses=IngredientReadSerializer),
    create=extend_schema(responses=IngredientReadSerializer),
    list=extend_schema(responses=IngredientReadSerializer),
    update=extend_schema(responses=IngredientReadSerializer),
    patch=extend_schema(responses=IngredientReadSerializer),
)
class IngredientViewset(viewsets.ModelViewSet):
    queryset = (
        Ingredient.objects.prefetch_related("category")
        .annotate(used_times=Count(F("recipe_ingredients")))
        .order_by(*Ingredient._meta.ordering or [])
        .all()
    )
    serializer_class = IngredientSerializer
    ordering_fields = [
        "title",
        "min_pack_size",
        "price",
        "need_buy",
        "edible",
        "used_times",
    ]
    search_fields = ["title", "description"]

    @extend_schema(
        responses=inline_serializer(
            "AmountTypes", {"types": fields.JSONField(), "convert": fields.JSONField(), "short": fields.JSONField()}
        )
    )
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
    queryset = RecipeIngredient.objects.order_by(*RecipeIngredient._meta.ordering or []).all()
    serializer_class = RecipeIngredientSerializer


class RegularIngredientViewset(viewsets.ModelViewSet):
    queryset = RegularIngredient.objects.order_by(*RegularIngredient._meta.ordering or []).all()
    serializer_class = RegularIngredientSerializer


class RecipeTagViewset(viewsets.ModelViewSet):
    queryset = RecipeTag.objects.order_by(*RecipeTag._meta.ordering or []).all()
    serializer_class = RecipeTagSerializer


class MealTimeViewset(viewsets.ModelViewSet):
    queryset = MealTime.objects.order_by(*MealTime._meta.ordering or []).all()
    serializer_class = MealTimeSerializer


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=RecipePlanWeekReadSerializer,
    ),
    update=extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=RecipePlanWeekReadSerializer,
    ),
    destroy=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)]),
    patch=extend_schema(responses=RecipePlanWeekReadSerializer),
    list=extend_schema(responses=RecipePlanWeekReadSerializer),
)
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
        else:
            try:
                year, week = pk.split("_")
            except ValueError:
                pass

        if year or week:
            plan_week, _ = self.queryset.get_or_create(year=year, week=week)
            return plan_week

        return super().get_object()


@extend_schema_view(
    retrieve=extend_schema(responses=RecipePlanReadSerializer),
    list=extend_schema(responses=RecipePlanReadSerializer),
)
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
    queryset = RecipeRating.objects.prefetch_related("user").order_by("-id")
    serializer_class = RecipeRatingSerializer


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=ProductListWeekReadSerializer,
    ),
    update=extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=ProductListWeekReadSerializer,
    ),
    destroy=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)]),
    patch=extend_schema(responses=ProductListWeekReadSerializer),
    list=extend_schema(responses=ProductListWeekReadSerializer),
)
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
        else:
            try:
                year, week = pk.split("_")
            except ValueError:
                pass

        if year or week:
            plan_week, _ = ProductListWeek.objects.get_or_create(year=year, week=week)
            return plan_week

        return super().get_object()

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=ProductListWeekReadSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def generate(self, request, pk=None):
        week = self.get_object()
        week_plan, _ = RecipePlanWeek.objects.get_or_create(year=week.year, week=week.week)
        update_plan_week(week_plan)

        return self.retrieve(request)


@extend_schema_view(
    retrieve=extend_schema(responses=ProductListItemReadSerializer),
    create=extend_schema(
        responses=ProductListItemReadSerializer,
    ),
    update=extend_schema(
        responses=ProductListItemReadSerializer,
    ),
    list=extend_schema(responses=ProductListItemReadSerializer),
)
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


class IngredientCategoryViewset(viewsets.ModelViewSet):
    queryset = IngredientCategory.objects.order_by(*IngredientCategory._meta.ordering or [])
    serializer_class = IngredientCategorySerializer


class ShopViewset(viewsets.ModelViewSet):
    queryset = Shop.objects.order_by(*Shop._meta.ordering or [])
    serializer_class = ShopSerializer


class StatsViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            "StatsList",
            {
                "recipes": fields.IntegerField(),
                "ingredients": fields.IntegerField(),
                "plans": fields.IntegerField(),
                "tasks": fields.IntegerField(),
            },
        )
    )
    def list(self, request):
        data = {
            "recipes": Recipe.objects.filter(is_archived=False).count(),
            "ingredients": Ingredient.objects.count(),
            "plans": RecipePlanWeek.objects.filter(plans__gte=1).distinct().count(),
            "tasks": Task.objects.count(),
        }
        return response.Response(data)
