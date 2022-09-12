from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from users.models import User
from users.serializers import ShortUserSerializer, UserSerializer

from recipes.models import (Ingredient, MealTime, ProductListItem,
                            ProductListWeek, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipePlanWeek,
                            RecipeRating, RecipeTag)
from recipes.services.measurings import MEASURING_SHORT, MEASURING_TYPES


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


class IngredientSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    ingredient = IngredientSerializer()
    amount_type_str = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = "__all__"

    def get_amount_type_str(self, obj: RecipeIngredient):
        return amount_str(obj.amount_type)

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
    short_description = serializers.SerializerMethodField()
    images = RecipeImageSerializer(many=True)
    tags = RecipeTagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    ratings = RecipeRatingSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ()
        read_only_fields = ("author",)
        depth = 2

    def to_representation(self, instance):
        self.fields["author"] = ShortUserSerializer()
        return super().to_representation(instance)


    def get_short_description(self, obj: Recipe):
        return obj.get_short_description()


class RecipeShortSerializer(RecipeSerializer):
    tags = None
    # ingredients = None
    ratings = None
    author = None

    class Meta(RecipeSerializer.Meta):
        exclude = list(RecipeSerializer.Meta.exclude) + ["author"]


class MealTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealTime
        fields = "__all__"
        depth = 1


class RecipePlanSerializer(serializers.ModelSerializer):
    # recipe = RecipeSerializer()
    # meal_time = MealTimeSerializer()

    class Meta:
        model = RecipePlan
        fields = "__all__"
        depth = 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["recipe"] = RecipeShortSerializer(instance.recipe).data
        representation["meal_time"] = MealTimeSerializer(instance.meal_time).data

        return representation


class RecipePlanWeekSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    plans = RecipePlanSerializer(many=True)

    class Meta:
        model = RecipePlanWeek
        fields = "__all__"
        depth = 1

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # rep["plans"] = RecipePlanSerializer(instance.plans.prefetch_related("meal_time").all(), many=True).data
        return rep


class ProductListItemSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    amount_type_str = serializers.SerializerMethodField()
    week = serializers.PrimaryKeyRelatedField(queryset=ProductListWeek.objects.all())

    class Meta:
        model = ProductListItem
        fields = "__all__"
        read_only_fields = ("is_auto", "ingredient", "ingredients", "created", "edited")
        # depth = 1

    def get_amount_type_str(self, obj: RecipeIngredient):
        return amount_str(obj.amount_type)


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["ingredient"] = IngredientSerializer(instance.ingredient).data
        representation["ingredients"] = RecipeIngredientWithRecipeSerializer(instance.ingredients, many=True).data

        return representation


class ProductListWeekSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    items = ProductListItemSerializer(many=True)

    class Meta:
        model = ProductListWeek
        fields = "__all__"
        depth = 1
