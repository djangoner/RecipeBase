from django.test import TestCase
from recipes.models import DESC_LENGTH, gen_uuid, get_default_comments, recipe_image_upload_to
from recipes.tests.factories import (
    IngredientCategoryFactory,
    IngredientFactory,
    MealTimeFactory,
    ProductListItemFactory,
    ProductListWeekFactory,
    RecipeFactory,
    RecipeImageFactory,
    RecipeIngredientFactory,
    RecipePlanFactory,
    RecipePlanWeekFactory,
    RecipeRatingFactory,
    RecipeTagFactory,
    RegularIngredientFactory,
    ShopFactory,
    ShopIngredientCategoryFactory,
)
from unittest.mock import patch


class ModelsTestCase(TestCase):
    @patch("uuid.uuid4")
    def test_gen_uuid(self, mock_fn):
        mock_fn.return_value = "mock_uuid"
        assert mock_fn() == "mock_uuid"

    def test_gen_uuid_real(self):
        uuid = gen_uuid()
        assert len(str(uuid)) == 36

    @patch("recipes.models.gen_uuid")
    def test_recipe_imaage_upload_to(self, mock_fn):
        recipe = RecipeImageFactory()
        mock_fn.return_value = "mock_uuid"
        assert recipe_image_upload_to(recipe, "example.jpg") == f"uploads/recipe_images/{recipe.pk}/mock_uuid.jpg"

    def test_default_comments(self):
        assert get_default_comments() == {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""}

    def test_recipe(self):
        recipe = RecipeFactory()
        assert str(recipe) == recipe.title

        recipe_long = RecipeFactory(content="a" * DESC_LENGTH)
        assert recipe_long.get_short_description() == "a" * DESC_LENGTH + "..."
        assert recipe_long.get_short_description(length=10) == "a" * 10 + "..."
        assert recipe_long.get_short_description(length=DESC_LENGTH + 1) == "a" * DESC_LENGTH

        recipe_content = RecipeFactory(short_description="short")
        assert recipe_content.get_short_description() == "short"

        recipe_content2 = RecipeFactory(short_description="a" * DESC_LENGTH)
        assert recipe_content2.get_short_description() == "a" * DESC_LENGTH + "..."

    def test_recipe_image(self):
        image_title = RecipeImageFactory(title="Title")
        assert str(image_title) == "Title"

        image_no_title = RecipeImageFactory(title="")
        assert str(image_no_title) == f"#{image_no_title.id} {image_no_title.image}"

    def test_ingredient(self):
        ing = IngredientFactory()
        assert str(ing) == ing.title

    def test_recipe_ingredient(self):
        ing = RecipeIngredientFactory(recipe=RecipeFactory())
        assert str(ing) == f"{ing.recipe}: {ing.ingredient}"

    def test_regular_ingredient(self):
        ing = RegularIngredientFactory()
        assert str(ing) == f"{ing.ingredient}"

    def test_recipe_tag(self):
        tag = RecipeTagFactory()
        assert str(tag) == tag.title
        assert tag.recipes_count() == 0

        recipe = RecipeFactory()
        recipe.tags.add(tag)
        assert tag.recipes_count() == 1

    def test_meal_time(self):
        meal_time = MealTimeFactory(time=None)
        assert str(meal_time) == meal_time.title

        meal_time2 = MealTimeFactory(time="12:00")
        meal_time2.time = "12:30"
        assert str(meal_time2) == f"{meal_time2.time} - {meal_time2.title}"

    def test_recipe_rating(self):
        rating = RecipeRatingFactory()
        assert str(rating) == f"{rating.recipe} {rating.user} - {rating.rating}"

    def test_recipe_plan_week(self):
        week = RecipePlanWeekFactory()
        assert str(week) == f"{week.year}-{week.week}"

    def test_recipe_plan(self):
        recipe_plan = RecipePlanFactory(week=RecipePlanWeekFactory())
        assert str(recipe_plan) == f"{recipe_plan.week}.{recipe_plan.day} {recipe_plan.meal_time}"

    def test_product_list_week(self):
        week = RecipePlanWeekFactory()
        assert str(week) == f"{week.year}-{week.week}"

    def test_product_list_item(self):
        item = ProductListItemFactory(week=ProductListWeekFactory())
        assert str(item) == f"{item.week}.{item.day} {item.title}"

    def test_shop(self):
        shop = ShopFactory()
        assert str(shop) == shop.title

    def test_ingredient_category(self):
        ingredient_category = IngredientCategoryFactory()
        assert str(ingredient_category) == ingredient_category.title

    def test_shop_ingredient_category(self):
        shop_category = ShopIngredientCategoryFactory()
        assert str(shop_category) == f"#{shop_category.num}"
