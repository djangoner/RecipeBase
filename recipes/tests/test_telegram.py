from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from recipes.models import ProductListItem, ProductListWeek, Recipe, RecipePlan, RecipePlanWeek
from recipes.services import telegram
from recipes.tests.factories import (
    ProductListItemFactory,
    ProductListWeekFactory,
    RecipeFactory,
    RecipeImageFactory,
    RecipePlanFactory,
    RecipePlanWeekFactory,
    RecipeRatingFactory,
)

telegram.BOT_TOKEN = "TEST_TOKEN"
telegram.SITE_DOMAIN = "http://example.com"


@pytest.fixture
def plan_week():
    return telegram.get_current_plan_week()


@pytest.fixture
def products_week():
    return telegram.get_current_product_week()


def test_get_notifications_dict():
    d = telegram.get_notifications_dict()
    for k, v in d.items():
        assert isinstance(k, str)
        assert isinstance(v, str)


def test_telegram_get_bot(mocker: MockerFixture):
    p = mocker.patch("telebot.TeleBot", return_value="ok")
    telegram.get_bot()
    p.assert_called_once_with("TEST_TOKEN", parse_mode="HTML")


def test_get_today_day():
    assert telegram.get_today_day() in range(1, 7)


@pytest.mark.django_db
def test_get_current_plan_week():
    week = telegram.get_current_plan_week()
    assert isinstance(week, RecipePlanWeek)
    assert week.year == datetime.now().year
    assert week.week == datetime.now().isocalendar()[1]


@pytest.mark.django_db
def test_get_current_product_week():
    week = telegram.get_current_product_week()
    assert isinstance(week, ProductListWeek)
    assert week.year == datetime.now().year
    assert week.week == datetime.now().isocalendar()[1]


@pytest.mark.django_db
def test_plan_items_filtered(mocker: MockerFixture):
    week: RecipePlanWeek = RecipePlanWeekFactory.create()

    RecipePlanFactory(week=week, recipe=None)
    RecipePlanFactory(week=week, day=1)
    plan1: RecipePlan = RecipePlanFactory.create(week=week, day=2)

    mocker.patch("recipes.services.telegram.get_today_day", return_value=2)
    res = telegram.get_plan_items_filtered(week)

    assert res == [plan1]


@pytest.mark.django_db
def test_get_product_list_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=None)
    ProductListItemFactory(week=week, day=1)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=2)

    mocker.patch("recipes.services.telegram.get_today_day", return_value=2)
    res = telegram.get_product_list_filtered(week)

    assert res == [plan1]


@pytest.mark.django_db
def test_get_product_list_on_week_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=1)
    ProductListItemFactory(week=week, day=2, is_completed=True)
    ProductListItemFactory(week=week, day=None, is_completed=True)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=None)
    plan2: ProductListItem = ProductListItemFactory.create(week=week, day=None)

    mocker.patch("recipes.services.telegram.get_today_day", return_value=3)
    res = telegram.get_product_list_on_week_filtered(week)

    assert res == [plan1, plan2]


@pytest.mark.django_db
def test_get_product_list_missed_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=5)
    ProductListItemFactory(week=week, day=3, is_completed=True)
    ProductListItemFactory(week=week, day=None, is_completed=True)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=1)
    plan2: ProductListItem = ProductListItemFactory.create(week=week, day=3)

    mocker.patch("recipes.services.telegram.get_today_day", return_value=3)
    res = telegram.get_product_list_missed_filtered(week)

    assert res == [plan1, plan2]


@pytest.mark.django_db
def test_get_recipe_flags():

    recipe_empty: Recipe = RecipeFactory.create()
    assert telegram.get_recipe_flags(recipe_empty) == [telegram.RecipeFlags.no_images, telegram.RecipeFlags.no_ratings]

    recipe_with_image: Recipe = RecipeFactory.create()
    RecipeImageFactory(recipe=recipe_with_image)
    assert telegram.get_recipe_flags(recipe_with_image) == [telegram.RecipeFlags.no_ratings]

    recipe_with_rating: Recipe = RecipeFactory.create()
    RecipeRatingFactory.create_batch(5, recipe=recipe_with_rating)
    assert telegram.get_recipe_flags(recipe_with_rating) == [telegram.RecipeFlags.no_images]

    recipe_with_all: Recipe = RecipeFactory.create()
    RecipeImageFactory.create(recipe=recipe_with_all)
    RecipeRatingFactory.create_batch(5, recipe=recipe_with_all)
    assert telegram.get_recipe_flags(recipe_with_all) == []
