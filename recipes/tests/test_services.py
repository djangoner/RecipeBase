import logging
from django.test import TestCase
from recipes.models import ProductListItem, ProductListWeek, RecipePlan

from recipes.services import plans, measurings
from recipes.tests.factories import IngredientFactory, RecipeIngredientFactory, RecipePlanWeekFactory

logging.disable(logging.CRITICAL)


class MeasuringsTestCase(TestCase):
    def test_short_text_short(self):
        assert not (measurings.short_text("X" * 50, 100).endswith("..."))

    def test_short_text_long(self):
        assert measurings.short_text("X" * 101, 100).endswith("...")

    def test_amount_to_grams(self):
        assert measurings.amount_to_grams(None, "g") == None
        assert measurings.amount_to_grams(1, "g") == 1
        assert measurings.amount_to_grams(1, "kg") == 1000
        assert measurings.amount_to_grams(4, "cup") == 1000
        assert measurings.amount_to_grams(500, "pinch") == 1000


class PlansConvertTestCase(TestCase):
    def test_is_convertable_true(self):
        assert plans.is_convertible("g") == True
        assert plans.is_convertible("kg") == True
        assert plans.is_convertible("l") == True
        assert plans.is_convertible("ml") == True
        assert plans.is_convertible("unknown") == False
        assert plans.is_convertible("l", advanced=False) == False
        assert plans.is_convertible("ml", advanced=False) == False

    def test_convert_grams_basic(self):
        # Basic
        assert plans.convert_all_to_grams([["g", 10]]) == ("g", 10)
        assert plans.convert_all_to_grams([["g", 10], ["g", 10]]) == ("g", 20)

    def test_convert_grams_advanced(self):
        # Advanced
        assert plans.convert_all_to_grams([["g", 100], ["kg", 1]]) == ("g", 1100)
        assert plans.convert_all_to_grams([["g", 100], ["kg", 1]]) == ("g", 1100)
        assert plans.convert_all_to_grams([["g", 100], ["cup", 1]]) == ("g", 250 + 100)
        assert plans.convert_all_to_grams([["kg", 1], ["cup", 1]]) == ("g", 1000 + 250)
        assert plans.convert_all_to_grams([["items", 1], ["cup", 1]]) == ("g", 0)  # Items are ignored

    def test_convert_grams_liquids(self):
        # Liquids
        assert plans.convert_all_to_grams([["ml", 100]]) == ("ml", 100)
        assert plans.convert_all_to_grams([["l", 10]]) == ("ml", 10_000)
        assert plans.convert_all_to_grams([["l", 1], ["ml", 100]]) == ("ml", 1000 + 100)

    def test_convert_grams_invalid(self):
        # Invalid
        assert plans.convert_all_to_grams([["g", None]]) == ("g", 0)
        assert plans.convert_all_to_grams([["g", None], ["cup", 1]]) == ("g", 250)
        assert plans.convert_all_to_grams([["ml", None]]) == ("g", 0)
        assert plans.convert_all_to_grams([["g", 1], ["ml", 1]]) == ("g", 0)
        assert plans.convert_all_to_grams([["cup", 1], ["l", 1]]) == ("g", 0)
        assert plans.convert_all_to_grams([["unknown", 1]]) == ("g", 0)
        assert plans.convert_all_to_grams([["unknown", 1]]) == ("g", 0)


class PlansGenerationTestCase(TestCase):
    def test_week_ingredients_basic(self):
        week = RecipePlanWeekFactory.create()
        assert week.plans.count() == 7

        ingredients = plans.get_week_ingredients(week)
        assert ingredients == {}

    def test_week_ingredients_advanced(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory()
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        RecipeIngredientFactory(recipe=week_plans[0].recipe, amount=100, amount_type="g", ingredient__need_buy=False)
        ings.append(
            RecipeIngredientFactory(recipe=week_plans[1].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        ingredients = plans.get_week_ingredients(week)
        self.assertDictEqual(
            ingredients,
            {
                ingredient.title: {
                    "measuring": None,
                    "amount": 0,
                    "amounts": [["g", 100], ["g", 100]],
                    "min_day": 1,
                    "ingredient": ingredient,
                    "ingredients": ings,
                }
            },
        )

    def test_plan_week_basic(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory()
        ings = []

        ings.append(
            RecipeIngredientFactory(recipe=week_plans[0].recipe, ingredient=ingredient, amount=100, amount_type="g")
        )

        plan_result = plans.get_plan_week_ingredients(week)
        self.assertDictEqual(
            plan_result,
            {
                ingredient.title: {
                    "measuring": "g",
                    "amount": 100,
                    "amounts": [["g", 100]],
                    "min_day": 1,
                    "ingredient": ingredient,
                    "ingredients": ings,
                }
            },
        )

    def test_plan_week_liquids(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory()
        ingredient2 = IngredientFactory()
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

        plan_result = plans.get_plan_week_ingredients(week)
        self.assertDictEqual(
            plan_result,
            {
                ingredient.title: {
                    "measuring": "ml",
                    "amount": 1100,
                    "amounts": [["l", 1], ["ml", 100]],
                    "min_day": 1,
                    "ingredient": ingredient,
                    "ingredients": ings,
                }
            },
        )

    def test_plan_week_items(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory(item_weight=150)
        ingredient2 = IngredientFactory()
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
        self.assertDictEqual(
            plan_result,
            {
                ingredient.title: {
                    "measuring": None,
                    "amount": 0,
                    "amounts": [["items", 1], ["g", 100]],
                    "min_day": 1,
                    "ingredient": ingredient,
                    "ingredients": ings,
                }
            },
        )

    def test_plan_week_any(self):
        week = RecipePlanWeekFactory.create()
        week_plans: list[RecipePlan] = week.plans.all()
        ingredient = IngredientFactory(item_weight=150)
        ingredient2 = IngredientFactory()
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
        self.assertDictEqual(
            plan_result,
            {
                ingredient.title: {
                    "measuring": "head",
                    "amount": 5,
                    "amounts": [["head", 1], ["head", 4]],
                    "min_day": 1,
                    "ingredient": ingredient,
                    "ingredients": ings,
                }
            },
        )

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

        item: ProductListItem = product_week.items.first()
        assert item.amount == 100
        assert item.amount_type == "g"
        assert item.ingredient == ingredient
        assert item.title == ingredient.title
        assert item.is_auto == True
        assert item.day == 0
        assert item.is_deleted == False

        # Test removing from product list
        week.plans.all().delete()
        week.plans.set([])

        product_week.refresh_from_db()
        plans.update_plan_week(week)
        assert product_week.items.count() == 0
