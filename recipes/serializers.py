from datetime import date, datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    IngredientCategory,
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
    RegularIngredient,
    Shop,
    ShopIngredientCategory,
    WeekPlanCondition,
)
from recipes.services.conditions import process_conditions_tree, warnings_json
from recipes.services.ingredients import (
    recipe_ingredient_packs,
    recipe_ingredient_price_full,
    recipe_ingredient_price_part,
)
from recipes.services.measurings import measuring_str
from users.models import User
from users.serializers import ShortUserSerializer
from rest_flex_fields import FlexFieldsModelSerializer


class StatusOkSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)


class RecipeImageSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)
    image_thumbnail_webp = serializers.ImageField(read_only=True)

    class Meta:
        model = RecipeImage
        fields = "__all__"
        # read_only_fields = ("image", )


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        exclude = ()


class ShopShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        exclude = ("category_sort",)


class ShopIngredientCategorySerializer(serializers.ModelSerializer):
    shop = ShopShortSerializer()

    class Meta:
        model = ShopIngredientCategory
        fields = "__all__"


class IngredientCategorySerializer(serializers.ModelSerializer):
    sorting = ShopIngredientCategorySerializer(many=True)

    class Meta:
        model = IngredientCategory
        fields = "__all__"


class RegularIngredientSerializer(serializers.ModelSerializer):
    amount_type_str = serializers.SerializerMethodField()

    class Meta:
        model = RegularIngredient
        fields = "__all__"

    @extend_schema_field(OpenApiTypes.STR)
    def get_amount_type_str(self, obj: RecipeIngredient):
        return measuring_str(obj.amount_type)


class IngredientSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer, serializers.ModelSerializer):
    used_times = serializers.SerializerMethodField()
    # category = IngredientCategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=IngredientCategory.objects.all(), required=False, allow_null=True, default=None
    )
    regular_ingredients = RegularIngredientSerializer(read_only=True)
    image = serializers.ImageField(max_length=None, allow_empty_file=True, allow_null=True, required=False)
    image_thumbnail = serializers.ImageField(read_only=True)
    image_thumbnail_webp = serializers.ImageField(read_only=True)

    class Meta:
        model = Ingredient
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_used_times(self, obj: Recipe):
        return getattr(obj, "used_times", None)


class IngredientReadSerializer(IngredientSerializer):
    pass
    # category = IngredientCategorySerializer()


class RecipeIngredientSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer, serializers.ModelSerializer):
    # ingredient = IngredientSerializer()
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount_type_str = serializers.SerializerMethodField()
    packs = serializers.SerializerMethodField()
    price_part = serializers.SerializerMethodField()
    price_full = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ingredient"] = IngredientSerializer(instance.ingredient).data if instance.ingredient else None
        return representation

    @extend_schema_field(OpenApiTypes.STR)
    def get_amount_type_str(self, obj: RecipeIngredient):
        return measuring_str(obj.amount_type)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_packs(self, obj: RecipeIngredient):
        return round(recipe_ingredient_packs(obj), 3)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_part(self, obj: ProductListItem):
        return recipe_ingredient_price_part(obj)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_full(self, obj: ProductListItem):
        return recipe_ingredient_price_full(obj)


class RecipeTagSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = "__all__"


class RecipeRatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = RecipeRating
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["user"] = ShortUserSerializer()
        return super().to_representation(instance)


class RecipeRatingReadSerializer(RecipeRatingSerializer):
    user = ShortUserSerializer()


class RecipeSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer, serializers.ModelSerializer):
    short_description_str = serializers.SerializerMethodField()
    last_cooked = serializers.SerializerMethodField()
    cooked_times = serializers.SerializerMethodField()
    is_planned = serializers.SerializerMethodField()
    images = RecipeImageSerializer(many=True, required=False)
    tags = RecipeTagSerializer(many=True, required=False)
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    ratings = RecipeRatingSerializer(many=True, required=False)
    author = ShortUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        exclude: tuple[str] | tuple = ()
        read_only_fields = ("author",)
        depth = 2

    # def to_representation(self, instance):
    #     self.fields["author"] = ShortUserSerializer()
    #     return super().to_representation(instance)

    @extend_schema_field(OpenApiTypes.STR)
    def get_short_description_str(self, obj: Recipe):
        return obj.get_short_description()

    @extend_schema_field(OpenApiTypes.DATE)
    def get_last_cooked(self, obj: Recipe) -> date | None:
        return getattr(obj, "last_cooked", None)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_cooked_times(self, obj: Recipe) -> int | None:
        return getattr(obj, "cooked_times", None)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_planned(self, obj: Recipe) -> bool:
        last_cooked = self.get_last_cooked(obj)
        if not last_cooked:
            return False

        now = datetime.now()
        now_week = now.isocalendar()[1]

        if now.isocalendar().weekday >= 5:  # After friday skip week
            now_week += 1

        recipe_week = last_cooked.isocalendar()[1]
        return now_week == recipe_week


class RecipeIngredientReadSerializer(RecipeIngredientSerializer):
    ingredient = IngredientSerializer()


class RecipeReadSerializer(RecipeSerializer):
    author = ShortUserSerializer(read_only=True)
    ratings = RecipeRatingReadSerializer(many=True, required=False)
    ingredients = RecipeIngredientReadSerializer(many=True, required=False)


class RecipeIngredientWithRecipeSerializer(RecipeIngredientSerializer):
    # def to_representation(self, instance):
    #     self.fields["recipe"] = RecipeSerializer()
    #     return super().to_representation(instance)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["recipe"] = RecipeForRecipeIngredientSerializer(instance.recipe).data
        return representation


class RecipeShortSerializer(RecipeSerializer):
    tags = None  # type: ignore
    # ingredients = None  # type: ignore
    # ratings = None  # type: ignore
    author = None  # type: ignore
    content = None  # type: ignore
    content_source = None  # type: ignore
    images = None  # type: ignore
    # is_planned = None  # type: ignore

    class Meta(RecipeSerializer.Meta):
        exclude = tuple(list(RecipeSerializer.Meta.exclude) + ["author", "content", "content_source", "tags"])


class RecipeForRecipeIngredientSerializer(RecipeShortSerializer):
    ingredients = None  # type: ignore
    ratings = None  # type: ignore


class RecipeIngredientWithRecipeReadSerializer(RecipeIngredientWithRecipeSerializer):
    ingredient = IngredientReadSerializer()
    recipe = RecipeShortSerializer()


class MealTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealTime
        fields = "__all__"
        depth = 1


class RecipePlanSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    class Meta:
        model = RecipePlan
        fields = "__all__"
        depth = 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["recipe"] = RecipeSerializer(instance.recipe).data
        # representation["recipe"] = RecipeShortSerializer(instance.recipe).data
        representation["meal_time"] = MealTimeSerializer(instance.meal_time).data

        return representation


class RecipePlanShortSerializer(RecipePlanSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # representation["recipe"] = RecipeSerializer(instance.recipe).data
        representation["recipe"] = RecipeShortSerializer(instance.recipe).data
        representation["meal_time"] = MealTimeSerializer(instance.meal_time).data

        return representation


class RecipePlanShortReadSerializer(RecipePlanShortSerializer):
    recipe = RecipeShortSerializer()
    meal_time = MealTimeSerializer()


class RecipePlanReadSerializer(RecipePlanSerializer):
    recipe = RecipeReadSerializer()
    meal_time = MealTimeSerializer()


class ConditionWarningSerializer(serializers.Serializer):
    condition = serializers.IntegerField()
    value_current = serializers.CharField()
    value_expected = serializers.CharField()
    plan = serializers.IntegerField()

    def get_fields(self):
        fields = super().get_fields()
        fields["childrens"] = ConditionWarningSerializer(many=True)
        return fields


class RecipePlanWeekSerializer(serializers.ModelSerializer):
    plans = RecipePlanShortSerializer(many=True, required=False)
    warnings = serializers.SerializerMethodField()
    edited_first = serializers.SerializerMethodField()
    edited_last = serializers.SerializerMethodField()

    class Meta:
        model = RecipePlanWeek
        fields = "__all__"
        depth = 1

    @extend_schema_field(ConditionWarningSerializer(many=True))
    def get_warnings(self, instance: RecipePlanWeek):
        res = process_conditions_tree(instance)
        warnings = warnings_json(res.warnings)
        return warnings

    @extend_schema_field(serializers.DateTimeField)
    def get_edited_first(self, instance: RecipePlanWeek):
        plans = instance.plans
        if not instance.is_filled:
            plans = plans.filter(created__gte=datetime.now().date())
        plan: RecipePlan | None = plans.order_by("created").first()
        return plan.created if plan else None

    @extend_schema_field(serializers.DateTimeField)
    def get_edited_last(self, instance: RecipePlanWeek):
        plans = instance.plans
        if not instance.is_filled:
            plans = plans.filter(created__gte=datetime.now().date())
        else:
            edited_first = self.get_edited_first(instance)
            if edited_first:
                plans = plans.filter(created__gt=edited_first)
        plan: RecipePlan | None = plans.order_by("created").last()
        return plan.created if plan else None


class RecipePlanWeekShortSerializer(RecipePlanWeekSerializer, serializers.ModelSerializer):
    plans = None  # type: ignore


class RecipePlanWeekReadSerializer(RecipePlanWeekSerializer):
    plans = RecipePlanReadSerializer(many=True)


class ProductListItemSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer, serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=False, allow_null=True, default=None
    )
    amount_type_str = serializers.SerializerMethodField()
    week = serializers.PrimaryKeyRelatedField(queryset=ProductListWeek.objects.all())
    packs = serializers.SerializerMethodField()
    price_part = serializers.SerializerMethodField()
    price_full = serializers.SerializerMethodField()

    class Meta:
        model = ProductListItem
        fields = "__all__"
        read_only_fields = ("is_auto", "ingredient", "ingredients", "amounts", "created", "edited")
        # depth = 1

    @extend_schema_field(OpenApiTypes.STR)
    def get_amount_type_str(self, obj: ProductListItem):
        return measuring_str(obj.amount_type)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["ingredient"] = IngredientSerializer(instance.ingredient).data if instance.ingredient else None
        representation["ingredients"] = RecipeIngredientWithRecipeSerializer(instance.ingredients, many=True).data

        return representation

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_packs(self, obj: RecipeIngredient):
        return round(recipe_ingredient_packs(obj), 3)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_part(self, obj: ProductListItem):
        return recipe_ingredient_price_part(obj)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_full(self, obj: ProductListItem):
        return recipe_ingredient_price_full(obj)


class ProductListItemReadSerializer(ProductListItemSerializer):
    ingredient = IngredientReadSerializer()
    ingredients = RecipeIngredientWithRecipeReadSerializer(many=True)


class ProductListWeekSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer, serializers.ModelSerializer):
    items = ProductListItemSerializer(many=True, required=False)

    class Meta:
        model = ProductListWeek
        fields = "__all__"
        depth = 1


class ProductListWeekReadSerializer(ProductListWeekSerializer):
    items = ProductListItemReadSerializer(many=True)


class ProductListWeekShortSerializer(ProductListWeekSerializer):
    items = None  # type: ignore


class WeekPlanConditionSerializer(serializers.ModelSerializer):
    full_day = serializers.SerializerMethodField()

    class Meta:
        model = WeekPlanCondition
        exclude = ()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_full_day(self, instance: WeekPlanCondition):
        return instance.full_day
