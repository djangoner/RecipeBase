from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer

from recipes.models import (Ingredient, MealTime, Recipe, RecipeImage,
                            RecipeIngredient, RecipePlan, RecipePlanWeek,
                            RecipeRating, RecipeTag)


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
        return obj.get_amount_type_display()


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
        self.fields['user'] = UserSerializer()
        return super().to_representation(instance)



class RecipeSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField()
    images = RecipeImageSerializer(many=True)
    tags = RecipeTagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    ratings = RecipeRatingSerializer(many=True)

    class Meta:
        model = Recipe
        fields = "__all__"
        depth = 2

    def get_short_description(self, obj: Recipe):
        return obj.get_short_description()


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

        representation["recipe"] = RecipeSerializer(instance.recipe).data
        representation["meal_time"] = MealTimeSerializer(instance.meal_time).data

        return representation



class RecipePlanWeekSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    plans = RecipePlanSerializer(many=True)

    class Meta:
        model = RecipePlanWeek
        fields = "__all__"
        depth = 1
