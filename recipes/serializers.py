import math
from datetime import date, datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from drf_writable_nested import WritableNestedModelSerializer
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
)
from recipes.services.measurings import MEASURING_SHORT, MEASURING_TYPES
from users.models import User
from users.serializers import ShortUserSerializer


def amount_str(meas: str):
    meas_types = dict(MEASURING_TYPES)
    if meas in MEASURING_SHORT:
        return MEASURING_SHORT[meas]
    elif meas in meas_types:
        return meas_types[meas]

    return meas


class RecipeImageSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = RecipeImage
        fields = "__all__"


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


class IngredientSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    used_times = serializers.SerializerMethodField()
    # category = IngredientCategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=IngredientCategory.objects.all(), required=False)

    class Meta:
        model = Ingredient
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["category"] = IngredientCategorySerializer(instance.category).data if instance.category else None
        return representation

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_used_times(self, obj: Recipe):
        return getattr(obj, "used_times", None)


class RecipeIngredientSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
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
        return amount_str(obj.amount_type)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_packs(self, obj: RecipeIngredient):
        if not (obj.amount and obj.ingredient and obj.ingredient.min_pack_size):
            return 0

        # if obj.amount_type == "items":
        #     return obj.amount
        return round(obj.amount / obj.ingredient.min_pack_size, 3)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_part(self, obj: RecipeIngredient):
        if not (
            obj.ingredient
            and (obj.ingredient.min_pack_size or obj.ingredient.item_weight)
            and obj.ingredient.price
            and obj.amount
        ):
            return

        packs = self.get_packs(obj)
        if obj.amount_type == "items" and obj.ingredient.item_weight:
            return round(packs * obj.ingredient.item_weight / obj.ingredient.min_pack_size)
        return round(packs * obj.ingredient.price)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_full(self, obj: RecipeIngredient):
        if not (
            obj.ingredient
            and (obj.ingredient.min_pack_size or obj.ingredient.item_weight)
            and obj.ingredient.price
            and obj.amount
        ):
            return

        packs = math.ceil(self.get_packs(obj))
        if obj.amount_type == "items" and obj.ingredient.item_weight:
            return round(obj.amount * obj.ingredient.item_weight / obj.ingredient.min_pack_size * obj.ingredient.price)
        return round(packs * obj.ingredient.price)


class RegularIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegularIngredient
        fields = "__all__"


class RecipeIngredientWithRecipeSerializer(RecipeIngredientSerializer):

    # def to_representation(self, instance):
    #     self.fields["recipe"] = RecipeSerializer()
    #     return super().to_representation(instance)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["recipe"] = RecipeShortSerializer(instance.recipe).data
        return representation


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


class RecipeSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    short_description_str = serializers.SerializerMethodField()
    last_cooked = serializers.SerializerMethodField()
    cooked_times = serializers.SerializerMethodField()
    is_planned = serializers.SerializerMethodField()
    images = RecipeImageSerializer(many=True, required=False)
    tags = RecipeTagSerializer(many=True, required=False)
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    ratings = RecipeRatingSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        exclude: tuple[str] | tuple = ()
        read_only_fields = ("author",)
        depth = 2

    def to_representation(self, instance):
        self.fields["author"] = ShortUserSerializer()
        return super().to_representation(instance)

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

        recipe_week = last_cooked.isocalendar()[1]
        return now_week == recipe_week


class RecipeShortSerializer(RecipeSerializer):
    tags = None  # type: ignore
    # ingredients = None
    ratings = None  # type: ignore
    author = None  # type: ignore

    class Meta(RecipeSerializer.Meta):
        exclude = tuple(list(RecipeSerializer.Meta.exclude) + ["author"])


class MealTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealTime
        fields = "__all__"
        depth = 1


class RecipePlanSerializer(serializers.ModelSerializer):
    # recipe = RecipeSerializer()
    # meal_time = MealTimeSerializer()
    full = False

    def __init__(self, *args, **kwargs) -> None:
        self.full = kwargs.pop("full", False)
        super().__init__(*args, **kwargs)

    class Meta:
        model = RecipePlan
        fields = "__all__"
        depth = 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if self.full:
            representation["recipe"] = RecipeSerializer(instance.recipe).data
        else:
            representation["recipe"] = RecipeShortSerializer(instance.recipe).data
        representation["meal_time"] = MealTimeSerializer(instance.meal_time).data

        return representation


class RecipePlanWeekSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    plans = RecipePlanSerializer(many=True, full=True)

    class Meta:
        model = RecipePlanWeek
        fields = "__all__"
        depth = 1


class RecipePlanWeekShortSerializer(RecipePlanWeekSerializer, serializers.ModelSerializer):
    plans = None  # type: ignore


class ProductListItemSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
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
        read_only_fields = ("is_auto", "ingredient", "ingredients", "created", "edited")
        # depth = 1

    @extend_schema_field(OpenApiTypes.STR)
    def get_amount_type_str(self, obj: ProductListItem):
        return amount_str(obj.amount_type)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["ingredient"] = IngredientSerializer(instance.ingredient).data if instance.ingredient else None
        representation["ingredients"] = RecipeIngredientWithRecipeSerializer(instance.ingredients, many=True).data

        return representation

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_packs(self, obj: ProductListItem):
        if not (obj.amount and obj.ingredient and obj.ingredient.min_pack_size):
            return 0

        # if obj.amount_type == "items":
        #     return obj.amount
        return round(obj.amount / obj.ingredient.min_pack_size, 3)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_part(self, obj: ProductListItem):
        if not (
            obj.ingredient
            and (obj.ingredient.min_pack_size or obj.ingredient.item_weight)
            and obj.ingredient.price
            and obj.amount
        ):
            return

        packs = self.get_packs(obj)
        if obj.amount_type == "items" and obj.ingredient.item_weight:
            return round(packs * obj.ingredient.item_weight / obj.ingredient.min_pack_size)
        return round(packs * obj.ingredient.price)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_price_full(self, obj: ProductListItem):
        if not (
            obj.ingredient
            and (obj.ingredient.min_pack_size or obj.ingredient.item_weight)
            and obj.ingredient.price
            and obj.amount
        ):
            return

        packs = math.ceil(self.get_packs(obj))
        if obj.amount_type == "items" and obj.ingredient.item_weight:
            return round(obj.amount * obj.ingredient.item_weight / obj.ingredient.min_pack_size * obj.ingredient.price)
        return round(packs * obj.ingredient.price)


class ProductListWeekSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    items = ProductListItemSerializer(many=True)

    class Meta:
        model = ProductListWeek
        fields = "__all__"
        depth = 1


class ProductListWeekShortSerializer(ProductListWeekSerializer):
    items = None  # type: ignore
