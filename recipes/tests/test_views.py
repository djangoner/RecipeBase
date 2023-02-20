import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from recipes.models import (
    Ingredient,
    IngredientCategory,
    MealTime,
    Recipe,
    RecipeIngredient,
    RecipePlan,
    RecipePlanWeek,
    RecipeRating,
    RecipeTag,
    Shop,
    ProductListWeek,
    ProductListItem,
)
from recipes.services.measurings import MEASURING_SHORT
from recipes.tests.factories import (
    IngredientFactory,
    ProductListItemFactory,
    ProductListWeekFactory,
    RecipeFactory,
    RecipeIngredientFactory,
    RecipePlanFactory,
    RecipePlanWeekFactory,
    RecipeRatingFactory,
)
from tasks.models import Task, TaskCategory
from django.utils.http import urlencode
from recipes.services import MEASURING_CONVERT, MEASURING_TYPES

logging.disable(logging.CRITICAL)


class RecipesTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(self) -> None:
        self.user = User.objects.create(username="testuser", is_superuser=True)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_stats_empty(self):
        resp = self.client.get("/api/v1/stats/")
        self.assertEqual(resp.status_code, 200)

        resp_json = resp.json()
        self.assertEqual(resp_json["recipes"], 0)
        self.assertEqual(resp_json["ingredients"], 0)
        self.assertEqual(resp_json["plans"], 0)
        self.assertEqual(resp_json["tasks"], 0)

    def test_stats_filled(self):
        # Recipes
        Recipe.objects.create(title="Counted", is_archived=False)
        Recipe.objects.create(title="Not counted", is_archived=True)

        # Ingredients
        Ingredient.objects.create(title="Counted")

        # Tasks
        task_category = TaskCategory.objects.create(title="Counted")
        Task.objects.create(title="Counted", category=task_category)

        # Reciple plans
        week1 = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")

        RecipePlan.objects.create(meal_time=meal_time, week=week1, day=1)

        ##

        resp = self.client.get("/api/v1/stats/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["recipes"], 1)
        self.assertEqual(resp_json["ingredients"], 1)
        self.assertEqual(resp_json["plans"], 1)
        self.assertEqual(resp_json["tasks"], 1)

    def test_recipes_list(self):
        Recipe.objects.create()
        resp = self.client.get("/api/v1/recipes/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_recipes_view(self):
        obj = Recipe.objects.create(title="Test recipe")
        resp = self.client.get(f"/api/v1/recipes/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test recipe")

    def test_recipes_compilation_archive(self):
        Recipe.objects.create(is_archived=True)
        Recipe.objects.create(is_archived=False)

        resp = self.client.get("/api/v1/recipes/", {"compilation": "archive"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)

    def test_recipes_compilation_vlong_uncooked(self):
        week = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")
        r1 = Recipe.objects.create(is_archived=True)
        r2 = Recipe.objects.create(is_archived=False)
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r1, day=1, date=datetime(2022, 1, 1))
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r2, day=1, date=datetime(2022, 1, 1))

        resp = self.client.get("/api/v1/recipes/", {"compilation": "vlong_uncooked"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        r1.is_archived = False
        r1.save()

        resp = self.client.get("/api/v1/recipes/", {"compilation": "vlong_uncooked"})
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 2)

    def test_recipes_compilation_long_uncooked(self):
        week = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")
        r1 = Recipe.objects.create(is_archived=True)
        r2 = Recipe.objects.create(is_archived=False)
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r1, day=1)
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r2, day=1)

        resp = self.client.get("/api/v1/recipes/", {"compilation": "long_uncooked"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 0)

    def test_recipes_compilation_top10(self):
        week = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")
        r1 = Recipe.objects.create(is_archived=True)
        r2 = Recipe.objects.create(is_archived=False)
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r1, day=1, date=datetime(2022, 1, 1))
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r2, day=1, date=datetime(2022, 1, 1))

        resp = self.client.get("/api/v1/recipes/", {"compilation": "top10"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        r1.is_archived = False
        r1.save()

        resp = self.client.get("/api/v1/recipes/", {"compilation": "top10"})
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 2)

    def test_recipes_compilation_new(self):
        week = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")
        r1 = RecipeFactory.create()  # Will be removed by filter
        RecipeFactory.create()  # Will be in results

        RecipePlanFactory.create(meal_time=meal_time, week=week, recipe=r1, day=1, date=datetime(2022, 1, 1))

        resp = self.client.get("/api/v1/recipes/", {"compilation": "new"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)

    def test_recipes_compilation_invalid(self):
        week = RecipePlanWeek.objects.create(year=2022, week=1)
        meal_time = MealTime.objects.create(title="Test")
        r1 = Recipe.objects.create()
        Recipe.objects.create()
        RecipePlan.objects.create(meal_time=meal_time, week=week, recipe=r1, day=1)

        resp = self.client.get("/api/v1/recipes/", {"compilation": "invalid_compilation"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 2)

    def create_test_ratings(self):
        r1 = Recipe.objects.create()
        r2 = Recipe.objects.create()
        r3 = Recipe.objects.create()
        r4 = Recipe.objects.create()
        r5 = Recipe.objects.create()

        RecipeRating.objects.create(recipe=r1, user=self.user, rating=1)
        RecipeRating.objects.create(recipe=r2, user=self.user, rating=2)
        RecipeRating.objects.create(recipe=r3, user=self.user, rating=3)
        RecipeRating.objects.create(recipe=r4, user=self.user, rating=4)
        RecipeRating.objects.create(recipe=r5, user=self.user, rating=5)

    def test_recipes_search_rating_gt(self):
        self.create_test_ratings()

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_+5"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_+1"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 5)

    def test_recipes_search_rating_lt(self):
        self.create_test_ratings()

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_-5"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 5)

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_-1"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

    def test_recipes_search_rating_eq(self):
        self.create_test_ratings()

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_3"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

        resp = self.client.get("/api/v1/recipes/", {"rating": f"{self.user.id}_1"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

    def test_recipes_search_rating_invalid(self):
        self.create_test_ratings()

        resp = self.client.get("/api/v1/recipes/", {"rating": "1"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 5)

    def test_recipes_search_tags_include(self):
        tag = RecipeTag.objects.create(title="Test")
        r1 = Recipe.objects.create()
        Recipe.objects.create()
        Recipe.objects.create()

        r1.tags.add(tag)

        resp = self.client.get("/api/v1/recipes/", {"tags_include": tag.id})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

    def test_recipes_search_tags_exclude(self):
        tag = RecipeTag.objects.create(title="Test")
        r1 = Recipe.objects.create()
        Recipe.objects.create()
        Recipe.objects.create()

        r1.tags.add(tag)

        resp = self.client.get("/api/v1/recipes/", {"tags_exclude": tag.id})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 2)

    def test_recipes_search_ingredients_include(self):
        ing = Ingredient.objects.create(title="Test")
        r1 = Recipe.objects.create()
        Recipe.objects.create()
        Recipe.objects.create()
        recipe_ing = RecipeIngredient.objects.create(ingredient=ing, recipe=r1, amount=1)

        r1.ingredients.add(recipe_ing)

        resp = self.client.get("/api/v1/recipes/", {"ingredients_include": recipe_ing.id})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 1)

    def test_recipes_search_ingredients_exclude(self):
        ing = Ingredient.objects.create(title="Test")
        r1 = Recipe.objects.create()
        Recipe.objects.create()
        Recipe.objects.create()
        recipe_ing = RecipeIngredient.objects.create(ingredient=ing, recipe=r1, amount=1)

        r1.ingredients.add(recipe_ing)

        resp = self.client.get("/api/v1/recipes/", {"ingredients_exclude": recipe_ing.id})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json["count"], 2)

    def test_recipes_create(self):
        resp = self.client.post("/api/v1/recipes/", {"title": "test recipe creation"})
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "test recipe creation")
        self.assertEqual(resp_json["author"]["id"], self.user.id)

    def test_recipe_ratings_list(self):
        RecipeRatingFactory(user=self.user)
        resp = self.client.get("/api/v1/recipe_rating/")
        self.assertEqual(resp.status_code, 200)

    def test_recipe_images_list(self):
        resp = self.client.get("/api/v1/recipe_images/")
        self.assertEqual(resp.status_code, 200)

    def test_recipe_tags_list(self):
        RecipeTag.objects.create(title="Test tag")
        resp = self.client.get("/api/v1/recipe_tags/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_recipe_tags_view(self):
        obj = RecipeTag.objects.create(title="Test tag")
        resp = self.client.get(f"/api/v1/recipe_tags/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test tag")

    def test_ingredients_list(self):
        Ingredient.objects.create(title="Test ingredient")
        resp = self.client.get("/api/v1/ingredients/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_ingredient_amount_types(self):
        resp = self.client.get(
            "/api/v1/ingredients/amount_types/",
        )
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        measuring_types = [{"id": k, "title": v} for k, v in MEASURING_TYPES]
        self.assertEqual(
            resp_json,
            {
                "types": measuring_types,
                "convert": MEASURING_CONVERT,
                "short": MEASURING_SHORT,
            },
        )

    def test_ingredients_view(self):
        obj = Ingredient.objects.create(title="Test ingredient")
        resp = self.client.get(f"/api/v1/ingredients/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test ingredient")

    def test_ingredient_category_list(self):
        IngredientCategory.objects.create(title="Test ingredient")
        resp = self.client.get("/api/v1/ingredient_category/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_ingredient_category_view(self):
        obj = IngredientCategory.objects.create(title="Test category")
        resp = self.client.get(f"/api/v1/ingredient_category/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test category")

    def test_meal_time_list(self):
        MealTime.objects.create(title="Test mealtime")
        resp = self.client.get("/api/v1/meal_time/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_meal_time_view(self):
        obj = MealTime.objects.create(title="Test mealtime")
        resp = self.client.get(f"/api/v1/meal_time/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test mealtime")

    def test_shop_list(self):
        Shop.objects.create(title="Test shop")
        resp = self.client.get("/api/v1/shop/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_shop_view(self):
        obj = Shop.objects.create(title="Test shop")
        resp = self.client.get(f"/api/v1/shop/{obj.id}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["title"], "Test shop")

    def test_recipe_plan_list(self):
        w = RecipePlanWeek.objects.create(year=2022, week=1)
        r = Recipe.objects.create()
        mtime = MealTime.objects.create(title="Meal")
        RecipePlan.objects.create(week=w, recipe=r, meal_time=mtime, day=1)
        resp = self.client.get("/api/v1/recipe_plan/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_recipe_plan_week_list(self):
        w = RecipePlanWeekFactory()
        RecipePlan(week=w, recipe=RecipeFactory())
        resp = self.client.get("/api/v1/recipe_plan_week/")
        self.assertEqual(resp.status_code, 200)
        # resp_json = resp.json()

        # self.assertEqual(resp_json["count"], 1)
        # self.assertEqual(resp_json["total_pages"], 1)

    def test_recipe_plan_week_current(self):
        RecipePlanWeekFactory()
        self.client.get("/api/v1/recipe_plan_week/now/")
        resp = self.client.get("/api/v1/recipe_plan_week/current/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        year, week = datetime.now().year, datetime.now().isocalendar()[1]

        self.assertEqual(resp_json["year"], year)
        self.assertEqual(resp_json["week"], week)

    def test_recipe_plan_week_by_week(self):
        w = RecipePlanWeek.objects.create(year=2022, week=1)
        resp = self.client.get(f"/api/v1/recipe_plan_week/{w.year}_{w.week}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["year"], 2022)
        self.assertEqual(resp_json["week"], 1)

    def test_recipe_plan_week_by_week_invalid(self):
        RecipePlanWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/recipe_plan_week/abc/")
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get("/api/v1/recipe_plan_week//")
        self.assertEqual(resp.status_code, 404)

    def test_recipe_plan_week_by_week_non_exists(self):
        RecipePlanWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/recipe_plan_week/1_1/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["year"], 1)
        self.assertEqual(resp_json["week"], 1)

    def test_product_week_list(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["count"], 1)
        self.assertEqual(resp_json["total_pages"], 1)

    def test_product_week_current(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/current/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        year, week = datetime.now().year, datetime.now().isocalendar()[1]

        self.assertEqual(resp_json["year"], year)
        self.assertEqual(resp_json["week"], week)

    def test_product_week_by_week(self):
        w = ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get(f"/api/v1/product_list_week/{w.year}_{w.week}/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["year"], 2022)
        self.assertEqual(resp_json["week"], 1)

    def test_product_week_by_week_invalid(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/abc/")
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get("/api/v1/product_list_week//")
        self.assertEqual(resp.status_code, 404)

    def test_product_week_by_week_non_exists(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/1_1/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(resp_json["year"], 1)
        self.assertEqual(resp_json["week"], 1)

    def test_product_week_generate(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/2022_1/generate/")
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertEqual(len(resp_json["items"]), 0)

    def test_recipe_week_short(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/recipe_plan_week/1_1/", {"short": "true"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertIsNone(resp_json.get("plans"))

    def test_product_week_short(self):
        ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.get("/api/v1/product_list_week/1_1/", {"short": "true"})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertIsNone(resp_json.get("items"))

    def test_product_week_move(self):
        week = ProductListWeek.objects.create(year=2022, week=1)
        week_new = ProductListWeek.objects.create(year=2022, week=2)
        item = ProductListItem.objects.create(week=week, day=1, title="Test")

        resp = self.client.post(
            f"/api/v1/product_list_item/{item.id}/move_week/",
            QUERY_STRING=urlencode({"week": week_new.id}),
        )
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()

        self.assertIsNotNone(resp_json["week"])
        self.assertEqual(resp_json["week"], week_new.id)

    def test_product_week_item_create(self):
        week = ProductListWeek.objects.create(year=2022, week=1)
        resp = self.client.post("/api/v1/product_list_item/", {"title": "test", "week": week.id})
        assert resp.status_code == 201
        resp_json = resp.json()

        assert resp_json["title"] == "test"
        assert resp_json["author"] == self.user.id

    def test_product_list_item(self):
        week = ProductListWeekFactory()
        ing = IngredientFactory(price=10, min_pack_size=100, item_weight=100)
        item1 = ProductListItemFactory(week=week, ingredient=ing, amount=1, amount_type="items")
        item1.ingredients.add(
            RecipeIngredientFactory(ingredient=ing, recipe=RecipeFactory(), amount=1, amount_type="items")
        )

        item2 = ProductListItemFactory(week=week, ingredient=ing)
        item2.ingredients.add(
            RecipeIngredientFactory(ingredient=ing, recipe=RecipeFactory(), amount=1, amount_type="items")
        )

        item3 = ProductListItemFactory(week=week, ingredient=ing, amount=1, amount_type="g")
        item3.ingredients.add(
            RecipeIngredientFactory(ingredient=ing, recipe=RecipeFactory(), amount=1, amount_type="g")
        )

        resp = self.client.get("/api/v1/product_list_item/")
        assert resp.status_code == 200

    def test_recipe_serializer(self):
        recipe = RecipeFactory()

        RecipeIngredientFactory(
            recipe=recipe,
            amount=1,
            amount_type="items",
            ingredient__price=10,
            ingredient__min_pack_size=100,
            ingredient__item_weight=100,
        )
        RecipeIngredientFactory(
            recipe=recipe,
            amount=100,
            amount_type="g",
            ingredient__price=10,
            ingredient__min_pack_size=100,
            ingredient__item_weight=100,
        )
        RecipeIngredientFactory(recipe=recipe, amount=1, amount_type="head")
        RecipeIngredientFactory(recipe=recipe, amount=1, amount_type="invalid")
        RecipeIngredientFactory(recipe=recipe)

        resp = self.client.get(
            f"/api/v1/recipes/{recipe.id}/",
        )
        assert resp.status_code == 200
