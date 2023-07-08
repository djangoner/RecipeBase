from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Optional

from recipes.models import (
    Ingredient,
    ProductListItem,
    ProductListWeek,
    Recipe,
    RecipeIngredient,
    RecipeIngredientRecommendation,
    RecipePlan,
    RecipePlanWeek,
    RegularIngredient,
)
from recipes.services.measurings import IngredientAmounts, convert_all_to_grams, is_convertible, measuring_str
from django.db import transaction

log = logging.getLogger("PlansGen")


@dataclass
class WeekIngredientInfo:
    ingredient: Ingredient
    ingredients: list[RecipeIngredient] = field(default_factory=list)
    measuring: Optional[str] = None
    amounts: IngredientAmounts = field(default_factory=list)
    amount: Optional[int | float] = None
    min_day: int = field(default=8)


def get_current_or_next_week():
    now = datetime.now()
    year, week = now.year, now.isocalendar()[1]

    if now.isocalendar()[2] >= 5:  # If friday
        week += 1

    if week > 54:
        year += 1
        week = 1

    return year, week


def get_ingredient_packs(ing: RecipeIngredient | ProductListItem) -> float | int:
    if not (ing.amount and ing.ingredient and ing.ingredient.min_pack_size):
        return 0

    # if obj.amount_type == "items":
    #     return obj.amount
    return round(ing.amount / ing.ingredient.min_pack_size, 3)


def get_default_ing() -> dict:
    return {
        "measuring": None,
        "amounts": list(),
        "amount": 0,
        "min_day": 7,
        "ingredient": None,
        "ingredients": list(),
    }


def get_ingredient_key(ing: RecipeIngredient):
    return ing.ingredient.title


def extract_ingredient_amount(ing: RecipeIngredient | RegularIngredient | RecipeIngredientRecommendation):
    if (
        ing.amount_type == "items" and ing.ingredient.item_weight and ing.ingredient.type != "item"
    ):  # Convert items to grams
        return ("g", int(ing.amount * ing.ingredient.item_weight))
    else:
        return (ing.amount_type, ing.amount)


def get_week_recipe_plans(week: RecipePlanWeek, recipe: Recipe) -> list[RecipePlan]:
    res: list[RecipePlan] = []

    for plan in week.plans.all():
        if plan.recipe.pk == recipe.pk:
            res.append(plan)

    return res


def get_week_recipe_min_day(week: RecipePlanWeek, recipe: Recipe) -> RecipePlan | None:
    plans = get_week_recipe_plans(week, recipe)
    if not plans:
        return None

    print("Plans: ", [p.day for p in plans])
    return min(plans, key=lambda x: x.day or 8)


def get_week_ingredients(week: RecipePlanWeek) -> dict[str, WeekIngredientInfo]:
    """Generate list of ingredients for week"""
    res: dict[str, WeekIngredientInfo] = {}

    # Add week plan ingredients
    plan: RecipePlan
    for plan in week.plans.all():
        plan.check_date()
        recipe = plan.recipe
        assert recipe is not None
        ingredients = recipe.ingredients.all()

        for ing in ingredients:
            ing_key = get_ingredient_key(ing)

            if not ing.ingredient.need_buy:  # Skip not required to buy ingredients
                continue

            if ing_key not in res:  # Create default ingredient
                res[ing_key] = WeekIngredientInfo(ingredient=ing.ingredient)
            ing_info = res[ing_key]

            # -- Add ingredient amount
            ing_info.amounts.append(extract_ingredient_amount(ing))

            ing_info.ingredients.append(ing)

            # -- Update ingredient min_day
            if plan.day and plan.day < ing_info.min_day:
                ing_info.min_day = plan.day

    # Add recommendations ingredients
    rec_ing: RecipeIngredientRecommendation
    for rec_ing in week.recommendations_ingredients.all():
        ing_key = rec_ing.ingredient.title
        if ing_key not in res:  # Create default ingredient
            min_day = 8
            if (min_plan := get_week_recipe_min_day(week, rec_ing.recipe)) is not None and min_plan.day:
                print("Min day set: ", min_plan.day)
                min_day = min_plan.day
            res[ing_key] = WeekIngredientInfo(ingredient=rec_ing.ingredient, min_day=min_day)

        res[ing_key].amounts.append(extract_ingredient_amount(rec_ing))

    # Add regular ingredients
    for regular_ing in RegularIngredient.get_active().all():
        ing_key = regular_ing.ingredient.title
        if ing_key not in res:  # Create default ingredient
            res[ing_key] = WeekIngredientInfo(ingredient=regular_ing.ingredient)
        ing_info = res[ing_key]

        ing_info.amounts.append(extract_ingredient_amount(regular_ing))
        if regular_ing.day and regular_ing.day < ing_info.min_day:
            ing_info.min_day = regular_ing.day

    return res


def get_plan_week_ingredients(week: RecipePlanWeek) -> dict[str, WeekIngredientInfo]:
    """Get summarized list of products for week"""

    ingredients = get_week_ingredients(week)

    # // Analyze amounts

    ing_name: str
    info: WeekIngredientInfo
    for ing_name, info in ingredients.items():
        # List of unique measuring types of ingredient
        amounts = info.amounts
        meas_types = list({measuring for measuring, amount in amounts})
        all_convert = all([is_convertible(m) for m in meas_types])
        all_any = len(meas_types) == 1

        # log.debug(
        #     f"Measurings: {meas_types}, all_convert: {all_convert}, all_any: {all_any}"
        # )
        if all_convert:  # If can convert all measurings to one
            meas, amount = convert_all_to_grams(amounts)
            info.measuring = meas
            info.amount = amount
        elif all_any:  # If all measurings are any
            info.measuring = meas_types[0]
            info.amount = sum([amount for meas, amount in amounts if amount])
        else:
            log.warning(f"Can't convert all measurings of {info.ingredient} ({meas_types}) to one!")

        # -- Check min pack size
        # if ing.min_pack_size:

        #     if not info["measuring"] in ["items"]:
        #         info["amount"] = (
        #             math.ceil(info["amount"] / ing.min_pack_size) * ing.min_pack_size
        #         )

    return ingredients


def get_ingredients_amounts(ingredients: list[RecipeIngredient]) -> dict[int, list]:
    amounts: dict[int, list] = {}
    ing: RecipeIngredient
    for ing in ingredients:
        if ing.recipe.pk not in amounts:
            amounts[ing.recipe.pk] = []

        amounts[ing.recipe.pk].append(
            {
                "amount": ing.amount,
                "amount_grams": ing.amount_grams,
                "amount_type": ing.amount_type,
                "amount_type_str": measuring_str(ing.amount_type),
                "is_main": ing.is_main,
            }
        )
    return amounts


def update_plan_week(week: RecipePlanWeek):
    ingredients = get_plan_week_ingredients(week)
    plan_week, _ = ProductListWeek.objects.get_or_create(year=week.year, week=week.week)
    edited_plans = []

    if ingredients is None or not isinstance(ingredients, dict):  # pragma: no cover
        log.warning(f"Strange ingredients: {ingredients}")
        return

    with transaction.atomic():
        for ing_name, ing_info in ingredients.items():
            # ing: RecipeIngredient = ing_info["ingredient"]

            plan_item: ProductListItem
            amounts = get_ingredients_amounts(ing_info.ingredients)

            plan_item, _ = plan_week.items.update_or_create(
                ingredient=ing_info.ingredient,
                is_auto=True,
                defaults={
                    "title": ing_name,
                    "amount": ing_info.amount,
                    "amounts": amounts,
                    "amount_type": ing_info.measuring,
                    "day": ing_info.min_day - 1,
                    "is_deleted": False,
                },
            )

            ids_curr = list(plan_item.ingredients.values_list("id", flat=True))
            ids_generated = [i.pk for i in ing_info.ingredients]
            if ids_curr != ids_generated:
                plan_item.ingredients.set(ing_info.ingredients)
                plan_item.save()
            edited_plans.append(plan_item.pk)

    old_items = plan_week.items.filter(is_auto=True).exclude(id__in=edited_plans)
    # old_items.update(is_deleted=True)
    old_items.delete()

    if not plan_week.is_actual:
        plan_week.is_actual = True
        plan_week.save(update_fields=["is_actual"])

    return ingredients
