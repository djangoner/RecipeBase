import logging
from datetime import datetime

from django.db.models import Count, F, Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import decorators, response, viewsets, permissions, exceptions
from django_auto_prefetching import AutoPrefetchViewSetMixin

# from django_q.tasks import async_task
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
    WeekPlanCondition,
)
from recipes.services.conditions import process_conditions_tree, warnings_json
from recipes.services.ingredients import recognize_ingredients_text
from recipes.services.plan_fill import PlanFill, PlanFillParams
from recipes.services.recommendations import (
    accept_recommendation,
    cancel_recommendation,
    find_recommendation,
    generate_recommendations,
)
from recipes.services.stats import get_week_stats
from recipes.services.utils import week_delta
from telegram_bot.services.notifications import send_notif_synced, send_product_list
from tasks.models import Task
from recipes.serializers import (
    ConditionWarningSerializer,
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
    RecipePlanWeekStatsSerializer,
    RecipeRatingSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeTagSerializer,
    IngredientCategorySerializer,
    RecognizedIngredientSerializer,
    RecommendationsSerializer,
    RegularIngredientSerializer,
    ShopSerializer,
    StatusOkSerializer,
    WeekPlanConditionSerializer,
)
from recipes.services.measurings import (
    MEASURING_CONVERT,
    MEASURING_SHORT,
    MEASURING_TYPES,
)
from recipes.services.plans import get_current_or_next_week, update_plan_week
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import fields


class SerializerKeyedMixin(viewsets.ModelViewSet):
    def get_serializer_class(self):
        self.request.GET.get("fields")


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
    price_part_gt = filters.NumberFilter("price_part", lookup_expr="gte")
    price_part_lt = filters.NumberFilter("price_part", lookup_expr="lte")
    price_full_gt = filters.NumberFilter("price_full", lookup_expr="gte")
    price_full_lt = filters.NumberFilter("price_full", lookup_expr="lte")

    difficulty_gt = filters.NumberFilter("difficulty", lookup_expr="gte")
    difficulty_lt = filters.NumberFilter("difficulty", lookup_expr="lte")

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
        for val in value.split(","):
            queryset = queryset.filter(tags=val)
        return queryset.distinct()

    def filter_tags_exclude(self, queryset, name, value: str):
        if not value:
            return queryset
        for val in value.split(","):
            queryset = queryset.exclude(tags=val)
        return queryset.distinct()

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
        elif value == "recent":
            week_firstday = timezone.now().today()
            while week_firstday.weekday() > 0:
                week_firstday = week_firstday - timezone.timedelta(days=1)
            qs = queryset.filter(
                last_cooked__gt=timezone.now() - timezone.timedelta(weeks=4),
                last_cooked__lt=week_firstday.date(),
            )
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
        elif value == "top10" or value == "popular":
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
    retrieve=extend_schema(
        responses=RecipeReadSerializer,
        parameters=[
            OpenApiParameter("omit", str),
        ],
    ),
    create=extend_schema(responses=RecipeReadSerializer),
    list=extend_schema(responses=RecipeReadSerializer),
    update=extend_schema(responses=RecipeReadSerializer),
    partial_update=extend_schema(responses=RecipeReadSerializer),
)
class RecipeViewset(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.prefetch_related(
            "author",
            "ratings",
            "ratings__user",
            "ingredients",
            "ingredients__ingredient",
            "ingredients__ingredient__regular_ingredients",
            "tags",
            "images",
            "ingredients__ingredient__regular_ingredients",
            "ingredients__ingredient__category",
            "ingredients__ingredient__category__sorting",
            "ingredients__ingredient__category__sorting__shop",
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
        "cooked_times",
        "price_part",
        "price_full",
        "?",
    ]

    def get_serializer_class(self):
        short = self.request.GET.get("short")

        if short:
            return RecipeShortSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        request=inline_serializer(
            "RecognizeText",
            {
                "text": fields.CharField(),
            },
        ),
        responses=inline_serializer(
            "RecognizedIngredients",
            {"result": RecognizedIngredientSerializer(many=True)},
        ),
    )
    @decorators.action(["POST"], detail=False)
    def recognize_ingredients(self, request):
        text = request.data.get("text", "")
        res = recognize_ingredients_text(text)
        if not res:
            return response.Response({"result": []})

        return response.Response({"result": [RecognizedIngredientSerializer(i).data for i in res]})


class RecipeImageViewset(viewsets.ModelViewSet):
    queryset = RecipeImage.objects.all()
    serializer_class = RecipeImageSerializer


class IngredientFilterSet(filters.FilterSet):
    # recipes__isnull = filters.BooleanFilter(method="filter_recipes", label="Рецепт is null")
    recipes__isnull = filters.BooleanFilter(field_name="recipe_ingredients", lookup_expr="isnull")

    class Meta:
        model = Ingredient
        fields = {
            "price": ["isnull"],
            # "recipes": ["isnull"],
            "need_buy": ["exact"],
            "edible": ["exact"],
            "category": ["exact", "isnull"],
        }


@extend_schema_view(
    retrieve=extend_schema(responses=IngredientReadSerializer),
    create=extend_schema(responses=IngredientReadSerializer),
    list=extend_schema(responses=IngredientReadSerializer),
    update=extend_schema(responses=IngredientReadSerializer),
    partial_update=extend_schema(responses=IngredientReadSerializer),
)
class IngredientViewset(viewsets.ModelViewSet):
    queryset = (
        Ingredient.objects.prefetch_related(
            "category", "category__sorting", "category__sorting__shop", "regular_ingredients"
        )
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
    filterset_class = IngredientFilterSet

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
    partial_update=extend_schema(responses=RecipePlanWeekReadSerializer),
    list=extend_schema(responses=RecipePlanWeekReadSerializer),
)
class RecipePlanWeekViewset(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
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
        "plans__recipe__ingredients__ingredient__regular_ingredients",
        "plans__recipe__ingredients__ingredient__category",
        "plans__recipe__ingredients__ingredient__category__sorting",
        "plans__recipe__ingredients__ingredient__category__sorting__shop",
        "recommendations_ingredients",
        "recommendations_ingredients__ingredient",
    )
    serializer_class = RecipePlanWeekSerializer
    search_fields = ["year", "week"]

    def get_serializer_class(self):
        short = self.request.GET.get("short")

        if short:
            return RecipePlanWeekShortSerializer

        return self.serializer_class

    def get_object(self, pk: str | None = None):
        pk = self.kwargs.get("pk", pk)
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

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=RecipePlanWeekStatsSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def stats(self, request, pk=None):
        plan = self.get_object()

        data = get_week_stats(plan)
        json = RecipePlanWeekStatsSerializer(data).data
        return response.Response(json)

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=ConditionWarningSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def warnings(self, request, pk=None):
        plan = self.get_object()

        conditions = process_conditions_tree(plan)
        warnings = warnings_json(conditions.warnings)
        return response.Response(warnings)

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=RecommendationsSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def recommendations(self, request, pk=None):
        plan = self.get_object()

        recommendations = generate_recommendations(plan).copy()

        data_json = []
        for i in recommendations:
            i.plan = i.plan.pk  # noqa
            data_json.append(RecommendationsSerializer(i).data)

        return response.Response(data_json)

    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH),
            OpenApiParameter("recommendation", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
        request=None,
        responses=StatusOkSerializer,
    )
    @decorators.action(["POST"], detail=True)
    def recommendation_accept(self, request, pk=None):
        plan = self.get_object()
        recommendation_id = request.GET.get("recommendation")

        if not recommendation_id:
            raise exceptions.ValidationError("Invalid empty recommendation", code="invalid_recommendation")

        # recommendation_obj = from_dict(data_class=data=recommendation)
        recommendation = find_recommendation(plan, recommendation_id)
        if not recommendation:
            raise exceptions.ValidationError("Invalid recommendation", code="invalid_recommendation")
        accept_recommendation(plan, recommendation)

        return response.Response({"ok": True})

    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH),
            OpenApiParameter("recommendation", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
        request=None,
        responses=StatusOkSerializer,
    )
    @decorators.action(["POST"], detail=True)
    def recommendation_cancel(self, request, pk=None):
        plan = self.get_object()
        recommendation_id = request.GET.get("recommendation")

        if not recommendation_id:
            raise exceptions.ValidationError("Invalid empty recommendation", code="invalid_recommendation")

        # recommendation_obj = from_dict(data_class=data=recommendation)
        recommendation = find_recommendation(plan, recommendation_id)
        if not recommendation:
            raise exceptions.ValidationError("Invalid recommendation", code="invalid_recommendation")
        cancel_recommendation(plan, recommendation)

        return response.Response({"ok": True})

    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH),
            # OpenApiParameter("recipes", OpenApiTypes.JSON_PTR, OpenApiParameter.QUERY),
        ],
        request=inline_serializer("PlaceRecipesList", {"recipes": fields.ListField(child=fields.IntegerField())}),
        responses=StatusOkSerializer,
    )
    @decorators.action(["POST"], detail=True)
    def place_recipes(self, request, pk=None):
        plan = self.get_object()
        recipes_ids: list[int] | None = request.data.get("recipes")

        if not recipes_ids:
            raise exceptions.ValidationError("Invalid recipes IDS", code="invalid_recipes")

        # recommendation_obj = from_dict(data_class=data=recommendation)
        recipes = list(Recipe.objects.filter(id__in=recipes_ids).all())
        recipes.sort(key=lambda x: recipes_ids.index(x.pk))

        params = PlanFillParams(recipes=recipes)
        plan_fill = PlanFill(plan, params)
        plan_fill.auto_arrange_recipes()

        return response.Response({"ok": True})


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
        "recipe__ingredients__ingredient__regular_ingredients",
        "recipe__ingredients__ingredient__category",
        "recipe__ingredients__ingredient__category__sorting",
        "recipe__ingredients__ingredient__category__sorting__shop",
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
    partial_update=extend_schema(responses=ProductListWeekReadSerializer),
    list=extend_schema(responses=ProductListWeekReadSerializer),
)
class ProductListWeekViewset(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
    queryset = ProductListWeek.objects.prefetch_related(
        "items",
        "items__author",
        "items__ingredient",
        "items__ingredients",
        "items__ingredients__ingredient",
        "items__ingredients__recipe",
        "items__ingredients__recipe__ingredients",
        "items__ingredients__recipe__ingredients__ingredient",
        "items__ingredients__recipe__tags",
        "items__ingredients__recipe__images",
        "items__ingredients__recipe__ingredients__ingredient__regular_ingredients",
        "items__ingredients__recipe__ingredients__ingredient__category",
        "items__ingredients__recipe__ingredients__ingredient__category__sorting",
        "items__ingredients__recipe__ingredients__ingredient__category__sorting__shop",
        "items__ingredients__ingredient__regular_ingredients",
        "items__ingredients__ingredient__category",
        "items__ingredients__ingredient__category__sorting",
        "items__ingredients__ingredient__category__sorting__shop",
        "items__ingredients__ingredient__regular_ingredients",
        "items__ingredient__category",
        "items__ingredient__category__sorting",
        "items__ingredient__category__sorting__shop",
        "items__ingredient__regular_ingredients",
    ).distinct()

    serializer_class = ProductListWeekSerializer
    search_fields = ["year", "week"]

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
            plan_week, _ = self.queryset.get_or_create(year=year, week=week)
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

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=StatusOkSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def send_list(self, request, pk=None):
        week = self.get_object()
        week_plan, _ = ProductListWeek.objects.get_or_create(year=week.year, week=week.week)

        # async_task("recipes.services.telegram.send_product_list", week_plan, request.user)
        send_product_list(week_plan, request.user)

        # return self.retrieve(request)
        return response.Response({"ok": True})

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=StatusOkSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def send_synced(self, request, pk=None):
        week = self.get_object()
        week_plan, _ = ProductListWeek.objects.get_or_create(year=week.year, week=week.week)

        # async_task("recipes.services.telegram.send_product_list", week_plan, request.user)
        send_notif_synced(week_plan, request.user)

        # return self.retrieve(request)
        return response.Response({"ok": True})

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        responses=StatusOkSerializer,
    )
    @decorators.action(["GET"], detail=True)
    def move_uncompleted(self, request, pk=None):
        week = self.get_object()
        week_plan, _ = ProductListWeek.objects.get_or_create(year=week.year, week=week.week)
        year, week = week_delta(week.year, week.week, -1)
        prev_list = ProductListWeek.objects.filter(year=year, week=week).first()

        prev_list.items.filter(is_auto=False, is_completed=False, already_completed=False).update(week=week_plan)
        return response.Response({"ok": True})


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
        "author",
        "ingredients",
        "ingredients__ingredient",
        "ingredients__recipe",
        "ingredients__recipe__ingredients",
        "ingredients__recipe__ingredients__ingredient",
        "ingredients__recipe__tags",
        "ingredients__recipe__images",
        "ingredients__recipe__ingredients__ingredient__regular_ingredients",
        "ingredients__recipe__ingredients__ingredient__category",
        "ingredients__recipe__ingredients__ingredient__category__sorting",
        "ingredients__recipe__ingredients__ingredient__category__sorting__shop",
        "ingredients__ingredient__regular_ingredients",
        "ingredients__ingredient__category",
        "ingredients__ingredient__category__sorting",
        "ingredients__ingredient__category__sorting__shop",
        "ingredients__ingredient__regular_ingredients",
        "ingredient__category",
        "ingredient__category__sorting",
        "ingredient__category__sorting__shop",
        "ingredient__regular_ingredients",
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
                #
                "year": fields.IntegerField(),
                "week": fields.IntegerField(),
                "week_plan_progress": fields.IntegerField(),
                "week_plan_filled": fields.IntegerField(),
                "week_product_progress": fields.IntegerField(),
                "week_product_filled": fields.IntegerField(),
            },
        )
    )
    def list(self, request):
        year, week = get_current_or_next_week()

        plan_week, _ = RecipePlanWeek.objects.get_or_create(year=year, week=week)
        product_week, _ = ProductListWeek.objects.get_or_create(year=year, week=week)

        plan_progress = plan_week.plans.filter(meal_time__is_primary=True).count() / (
            MealTime.objects.filter(is_primary=True).count() * 5
        )

        product_items = product_week.items.filter(already_completed=False)

        product_progress = 0
        if products_count := product_items.count():
            product_progress = product_items.filter(is_completed=True).count() / products_count

        data = {
            "recipes": Recipe.objects.filter(is_archived=False).count(),
            "ingredients": Ingredient.objects.count(),
            "plans": RecipePlanWeek.objects.filter(plans__gte=1).distinct().count(),
            "tasks": Task.objects.count(),
            "year": year,
            "week": week,
            "week_plan_progress": round(plan_progress, 2),
            "week_plan_filled": plan_week.is_filled,
            "week_product_progress": round(product_progress, 2),
            "week_product_filled": product_week.is_filled,
        }
        return response.Response(data)


class WeekPlanConditionViewset(viewsets.ModelViewSet):
    queryset = WeekPlanCondition.objects.all()
    serializer_class = WeekPlanConditionSerializer
