import logging
from django.test import SimpleTestCase, TestCase
from recipes.models import Ingredient, ProductListWeek, RecipePlan

from recipes.services import plans, measurings
from recipes.tests.factories import (
    IngredientFactory,
    RecipeIngredientFactory,
    RecipePlanWeekFactory,
    RegularIngredientFactory,
)

logging.disable(logging.CRITICAL)


class MeasuringsTestCase(SimpleTestCase):
    def test_short_text_short(self):
        assert not (measurings.short_text("X" * 50, 100).endswith("..."))

    def test_short_text_long(self):
        assert measurings.short_text("X" * 101, 100).endswith("...")

    def test_amount_to_grams(self):
        assert measurings.amount_to_grams(None, "g") is None
        assert measurings.amount_to_grams(1, "g") == 1
        assert measurings.amount_to_grams(1, "kg") == 1000
        assert measurings.amount_to_grams(4, "cup") == 1000
        assert measurings.amount_to_grams(500, "pinch") == 1000


class PlansConvertTestCase(TestCase):
    def test_is_convertible_true(self):
        assert plans.is_convertible("g") is True
        assert plans.is_convertible("kg") is True
        assert plans.is_convertible("l") is True
        assert plans.is_convertible("ml") is True
        assert plans.is_convertible("unknown") is False
        assert plans.is_convertible("l", advanced=False) is False
        assert plans.is_convertible("ml", advanced=False) is False

    def test_convert_grams_basic(self):
        # Basic
        assert plans.convert_all_to_grams([("g", 10)]) == ("g", 10)
        assert plans.convert_all_to_grams([("g", 10), ("g", 10)]) == ("g", 20)

    def test_convert_grams_advanced(self):
        # Advanced
        assert plans.convert_all_to_grams([("g", 100), ("kg", 1)]) == ("g", 1100)
        assert plans.convert_all_to_grams([("g", 100), ("kg", 1)]) == ("g", 1100)
        assert plans.convert_all_to_grams([("g", 100), ("cup", 1)]) == ("g", 250 + 100)
        assert plans.convert_all_to_grams([("kg", 1), ("cup", 1)]) == ("g", 1000 + 250)
        assert plans.convert_all_to_grams([("items", 1), ("cup", 1)]) == ("g", 0)  # Items are ignored

    def test_convert_grams_liquids(self):
        # Liquids
        assert plans.convert_all_to_grams([("ml", 100)]) == ("ml", 100)
        assert plans.convert_all_to_grams([("l", 10)]) == ("ml", 10_000)
        assert plans.convert_all_to_grams([("l", 1), ("ml", 100)]) == ("ml", 1000 + 100)

    def test_convert_grams_invalid(self):
        # Invalid
        assert plans.convert_all_to_grams([("g", None)]) == ("g", 0)
        assert plans.convert_all_to_grams([("g", None), ("cup", 1)]) == ("g", 250)
        assert plans.convert_all_to_grams([("ml", None)]) == ("g", 0)
        assert plans.convert_all_to_grams([("g", 1), ("ml", 1)]) == ("ml", 2)
        assert plans.convert_all_to_grams([("cup", 1), ("l", 1)]) == ("g", 0)
        assert plans.convert_all_to_grams([("unknown", 1)]) == ("g", 0)
        assert plans.convert_all_to_grams([("unknown", 1)]) == ("g", 0)


class PlansGenerationTestCase(TestCase):
    def test_week_ingredients_basic(self):
        week = RecipePlanWeekFactory.create()
        assert week.plans.count() == 7

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {}

    def test_week_ingredients_advanced(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create()
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        RecipeIngredientFactory(recipe=week_plans[0].recipe, amount=100, amount_type="g", ingredient__need_buy=False)
        ings.append(
            RecipeIngredientFactory(recipe=week_plans[1].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                measuring=None,
                amount=None,
                amounts=[("g", 100.0), ("g", 100.0)],
                min_day=1,
            )
        }

    def test_week_ingredients_items(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create(min_pack_size=200, item_weight=100)
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=2, amount_type="items")
        )

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                measuring=None,
                amount=None,
                amounts=[("g", 100.0), ("g", 200.0)],
                min_day=1,
            )
        }

    def test_week_regular_ingredient(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create()
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[1].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        RecipeIngredientFactory(recipe=week_plans[1].recipe, amount=100, amount_type="g", ingredient__need_buy=False)
        ings.append(
            RecipeIngredientFactory(recipe=week_plans[2].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        RegularIngredientFactory(ingredient=ingredient, day=1, amount=150, amount_type="g")

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                amounts=[("g", 100), ("g", 100), ("g", 150)],
                min_day=1,
            )
        }

    def test_week_regular_ingredient_only(self):
        week = RecipePlanWeekFactory.create()
        # week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create()
        ingredient2: Ingredient = IngredientFactory.create()
        ings = []

        RegularIngredientFactory(ingredient=ingredient, day=2, amount=150, amount_type="g")
        RegularIngredientFactory(ingredient=ingredient2, amount=50, amount_type="g")

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                amounts=[("g", 150.0)],
                min_day=2,
            ),
            ingredient2.title: plans.WeekIngredientInfo(
                ingredient=ingredient2,
                ingredients=ings,
                amounts=[("g", 50.0)],
                min_day=7,
            ),
        }

    def test_plan_week_basic(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create()
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        plan_result = plans.get_plan_week_ingredients(week)
        assert plan_result == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                measuring="g",
                amount=100,
                amounts=[("g", 100)],
                min_day=1,
            )
        }

    def test_plan_week_liquids(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create(item_weight=100)
        ings = []

        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[0].recipe, ingredient=ingredient, amount=1, amount_type="l"
            )
        )
        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[1].recipe, ingredient=ingredient, amount=100, amount_type="ml"
            )
        )
        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[1].recipe, ingredient=ingredient, amount=1, amount_type="items"
            )
        )

        plan_result = plans.get_plan_week_ingredients(week)
        assert plan_result == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                measuring="ml",
                amount=1200,
                amounts=[("l", 1), ("ml", 100), ("g", 100)],
                min_day=1,
            )
        }

    def test_plan_week_items(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create(item_weight=150)
        ings = []

        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[0].recipe, ingredient=ingredient, amount=1, amount_type="items"
            )
        )
        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[1].recipe, ingredient=ingredient, amount=100, amount_type="g"
            )
        )

        plan_result = plans.get_plan_week_ingredients(week)
        assert plan_result == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                measuring="g",
                amount=250,
                amounts=[("g", 150), ("g", 100)],
                min_day=1,
            )
        }

    def test_plan_week_any(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient: Ingredient = IngredientFactory.create(item_weight=150)
        ings = []

        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[0].recipe, ingredient=ingredient, amount=1, amount_type="head"
            )
        )
        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[1].recipe, ingredient=ingredient, amount=4, amount_type="head"
            )
        )

        plan_result = plans.get_plan_week_ingredients(week)
        assert plan_result == {
            ingredient.title: plans.WeekIngredientInfo(
                ingredient=ingredient,
                ingredients=ings,
                min_day=1,
                measuring="head",
                amount=5.0,
                amounts=[("head", 1.0), ("head", 4.0)],
            )
        }

    def test_update_plan_week_invalid(self):
        week = RecipePlanWeekFactory.create()
        week.plans.set([])
        week.save()
        res_ingredients = plans.update_plan_week(week)

        assert res_ingredients == {}

    def test_update_plan_week(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory()
        ings = []

        ings.append(
            RecipeIngredientFactory.create(
                recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g"
            )
        )
        plans.update_plan_week(week)
        product_week: ProductListWeek = ProductListWeek.objects.get(year=week.year, week=week.week)
        assert product_week.items.count() == 1

        item = product_week.items.first()
        assert item is not None
        assert item.amount == 100
        assert item.amount_type == "g"
        assert item.ingredient == ingredient
        assert item.title == ingredient.title
        assert item.is_auto is True
        assert item.day == 0
        assert item.is_deleted is False

        # Test removing from product list
        week.plans.all().delete()
        week.plans.set([])

        product_week.refresh_from_db()
        plans.update_plan_week(week)
        assert product_week.items.count() == 0
