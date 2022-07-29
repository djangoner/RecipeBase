import logging
import math
from typing import List, Tuple

from recipes.models import (Ingredient, ProductListItem, ProductListWeek,
                            RecipeIngredient, RecipePlan, RecipePlanWeek)
from recipes.services.measurings import MEASURING_CONVERT, amount_to_grams

log = logging.getLogger("PlansGen")
CONVERT_ADVANCED = ["l", "ml"]


def is_convertable(measuring: str, advanced: bool = True) -> bool:
    return measuring in MEASURING_CONVERT or (
        advanced and measuring in CONVERT_ADVANCED
    )


def convert_all_to_grams(measurings: List[Tuple[str, int]]) -> Tuple[str, int]:
    res: float = 0
    all_meas = "g"

    for meas, amount in measurings:

        if is_convertable(meas, advanced=False):
            amount_grams = amount_to_grams(amount, meas)
            if amount_grams:
                res += amount_grams
        elif meas == "l":
            res += amount * 1000
            all_meas = "ml"
        elif meas == "ml":
            res += amount
            all_meas = "ml"
        elif meas == "items":
            res += amount

    return all_meas, res


def get_plan_week(week: RecipePlanWeek) -> dict:
    """Get list of products for week"""

    res = {}

    ## // Generate list of ingredients for week

    for plan in week.plans.all():
        plan: RecipePlan
        recipe = plan.recipe
        ingredients = recipe.ingredients.all()

        for ing in ingredients:
            ing: RecipeIngredient
            ing_name = ing.ingredient.title

            if not ing.ingredient.need_buy:  # Skip not required to buy ingredients
                return

            if not ing_name in res:  # Create default ingredient
                res[ing_name] = {
                    "measuring": None,
                    "amounts": [],
                    "amount": 0,
                    "min_day": 7,
                    "ingredient": ing.ingredient,
                    "ingredients": [],
                }

            # -- Add ingredient amount
            res[ing_name]["amounts"].append([ing.amount_type, ing.amount])
            res[ing_name]["ingredients"].append(ing)

            # -- Update ingredient min_day
            if plan.day < res[ing_name]["min_day"]:
                res[ing_name]["min_day"] = plan.day

    ## // Analyze amounts

    for ing_name, info in res.items():

        # List of unique measuring types of ingredient
        ing = info["ingredient"]
        amounts = info["amounts"]
        meas_types = list(set([measuring for measuring, amount in amounts]))
        all_convert = all([is_convertable(m) for m in meas_types])
        all_any = len(meas_types) == 1

        # log.debug(
        #     f"Measurings: {meas_types}, all_convert: {all_convert}, all_any: {all_any}"
        # )
        if all_convert:  # If can convert all measurings to one
            meas, amount = convert_all_to_grams(amounts)
            info["measuring"] = meas
            info["amount"] = amount
        elif all_any:  # If all measurings are any
            info["measuring"] = meas_types[0]
            info["amount"] = sum([amount for meas, amount in amounts])
        else:
            log.warning(f"Can't convert all measurings of {ing} ({meas_types}) to one!")

        # -- Check min pack size
        if ing.min_pack_size:

            if not info["measuring"] in ["items"]:
                info["amount"] = (
                    math.ceil(info["amount"] / ing.min_pack_size) * ing.min_pack_size
                )

    return res


def update_plan_week(week: RecipePlanWeek):
    ingredients = get_plan_week(week)

    plan_week, _ = ProductListWeek.objects.get_or_create(year=week.year, week=week.week)

    edited_plans = []

    if not ingredients or not isinstance(ingredients, dict):
        log.warning(f"Strange ingredients: {ingredients}")
        return

    for ing_name, ing_info in ingredients.items():
        ing: RecipeIngredient = ing_info["ingredient"]

        plan_item, _ = plan_week.items.update_or_create(
            ingredient=ing_info["ingredient"],
            is_auto=True,
            defaults={
                "title": ing_name,
                "amount": ing_info["amount"],
                "amount_type": ing_info["measuring"],
                "day": ing_info["min_day"] - 1,
                "is_deleted": False,
            },
        )
        plan_item: ProductListItem
        plan_item.ingredients.set(ing_info["ingredients"])
        plan_item.save()
        edited_plans.append(plan_item.id)

    old_items = plan_week.items.exclude(id__in=edited_plans)
    old_items.update(is_deleted=True)

    return ingredients
