from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from recipes.models import ProductListItem, ProductListWeek, Recipe, RecipePlan, RecipePlanWeek
from telegram_bot.services import utils, telegram_handlers
from recipes.tests.factories import (
    ProductListItemFactory,
    ProductListWeekFactory,
    RecipeFactory,
    RecipeImageFactory,
    RecipePlanFactory,
    RecipePlanWeekFactory,
    RecipeRatingFactory,
)

utils.BOT_TOKEN = "TEST_TOKEN"
utils.SITE_DOMAIN = "http://example.com"


@pytest.fixture
def plan_week():
    return utils.get_current_plan_week()


@pytest.fixture
def products_week():
    return utils.get_current_product_week()


def test_get_notifications_dict():
    d = utils.get_notifications_dict()
    for k, v in d.items():
        assert isinstance(k, str)
        assert isinstance(v, str)


def test_telegram_get_bot(mocker: MockerFixture):
    p = mocker.patch("telebot.TeleBot", return_value="ok")
    telegram_handlers._get_bot()
    p.assert_called_once()
    # p.assert_called_once_with("TEST_TOKEN", parse_mode="HTML", use_class_middlewares=True)


def test_get_today_day():
    assert utils.get_today_day() in range(1, 7 + 1)


@pytest.mark.django_db
def test_get_current_plan_week():
    week = utils.get_current_plan_week()
    assert isinstance(week, RecipePlanWeek)
    assert week.year == datetime.now().year
    assert week.week == datetime.now().isocalendar()[1]


@pytest.mark.django_db
def test_get_current_product_week():
    week = utils.get_current_product_week()
    assert isinstance(week, ProductListWeek)
    assert week.year == datetime.now().year
    assert week.week == datetime.now().isocalendar()[1]


@pytest.mark.django_db
def test_plan_items_filtered(mocker: MockerFixture):
    week: RecipePlanWeek = RecipePlanWeekFactory.create()

    RecipePlanFactory(week=week, recipe=None)
    RecipePlanFactory(week=week, day=1)
    plan1: RecipePlan = RecipePlanFactory.create(week=week, day=2)

    mocker.patch("telegram_bot.services.utils.get_today_day", return_value=2)
    res = utils.get_plan_items_filtered(week)

    assert res == [plan1]


@pytest.mark.django_db
def test_get_product_list_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=None)
    ProductListItemFactory(week=week, day=1)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=2)

    mocker.patch("telegram_bot.services.utils.get_today_day", return_value=2)
    res = utils.get_product_list_filtered(week)

    assert res == [plan1]


@pytest.mark.django_db
def test_get_product_list_on_week_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=1)
    ProductListItemFactory(week=week, day=2, is_completed=True)
    ProductListItemFactory(week=week, day=2)
    ProductListItemFactory(week=week, day=3)
    ProductListItemFactory(week=week, day=None, is_completed=True)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=None)
    plan2: ProductListItem = ProductListItemFactory.create(week=week, day=None)
    plan3: ProductListItem = ProductListItemFactory.create(week=week, day=4)

    mocker.patch("telegram_bot.services.utils.get_today_day", return_value=3)
    res = utils.get_product_list_on_week_filtered(week)

    assert res == [plan1, plan2, plan3]


@pytest.mark.django_db
def test_get_product_list_missed_filtered(mocker: MockerFixture):
    week: ProductListWeek = ProductListWeekFactory.create()

    ProductListItemFactory(week=week, day=5)
    ProductListItemFactory(week=week, day=3, is_completed=True)
    ProductListItemFactory(week=week, day=None, is_completed=True)
    plan1: ProductListItem = ProductListItemFactory.create(week=week, day=1)
    plan2: ProductListItem = ProductListItemFactory.create(week=week, day=3)

    mocker.patch("telegram_bot.services.utils.get_today_day", return_value=3)
    res = utils.get_product_list_missed_filtered(week)

    assert res == [plan1, plan2]


@pytest.mark.django_db
def test_get_recipe_flags():

    recipe_empty: Recipe = RecipeFactory.create()
    assert utils.get_recipe_flags(recipe_empty) == [utils.RecipeFlags.no_images, utils.RecipeFlags.no_ratings]

    recipe_with_image: Recipe = RecipeFactory.create()
    RecipeImageFactory(recipe=recipe_with_image)
    assert utils.get_recipe_flags(recipe_with_image) == [utils.RecipeFlags.no_ratings]

    recipe_with_rating: Recipe = RecipeFactory.create()
    RecipeRatingFactory.create_batch(5, recipe=recipe_with_rating)
    assert utils.get_recipe_flags(recipe_with_rating) == [utils.RecipeFlags.no_images]

    recipe_with_all: Recipe = RecipeFactory.create()
    RecipeImageFactory.create(recipe=recipe_with_all)
    RecipeRatingFactory.create_batch(5, recipe=recipe_with_all)
    assert utils.get_recipe_flags(recipe_with_all) == []
