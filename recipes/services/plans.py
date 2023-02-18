import logging
from typing import List, Tuple

from recipes.models import (
    ProductListItem,
    ProductListWeek,
    RecipeIngredient,
    RecipePlan,
    RecipePlanWeek,
    RegularIngredient,
)
from recipes.serializers import amount_str
from recipes.services.measurings import MEASURING_CONVERT, MEASURING_LIQUIDS, amount_to_grams

log = logging.getLogger("PlansGen")
CONVERT_ADVANCED = ["l", "ml"]


def is_convertible(measuring: str, advanced: bool = True) -> bool:
    return measuring in MEASURING_CONVERT or (advanced and measuring in CONVERT_ADVANCED)


def convert_all_to_grams(measurings: List[Tuple[str, int]]) -> Tuple[str, int | float]:
    res: float = 0
    all_meas = "g"

    non_empty = list(filter(lambda m: m[1], measurings))
    all_liquids = all([meas in MEASURING_LIQUIDS for meas, amount in non_empty])
    all_normal = all([is_convertible(meas, advanced=False) for meas, amount in non_empty])

    for meas, amount in measurings:
        if not amount:
            continue

        if all_liquids:
            if meas == "l":
                res += amount * 1000
                all_meas = "ml"
            elif meas == "ml":
                res += amount
                all_meas = "ml"
            else:
                logging.debug(f"[liquids]Invalid measuring: {meas}")  # pragma: no cover
        elif all_normal:
            if is_convertible(meas, advanced=False):
                amount_grams = amount_to_grams(amount, meas)
                res += amount_grams
            # elif meas == "items":
            #     res += amount
            else:
                logging.debug(f"[grams]Invalid measuring: {meas}")  # pragma: no cover
        else:
            logging.debug(f"[mixed]Invalid measuring: {meas}")

    return all_meas, res


def get_default_ing() -> dict:
    return {
        "measuring": None,
        "amounts": list(),
        "amount": 0,
        "min_day": 7,
        "ingredient": None,
        "ingredients": list(),
    }


def get_week_ingredients(week: RecipePlanWeek) -> dict[str, dict]:
    """Generate list of ingredients for week"""
    res = {}

    # Add week plan ingredients
    plan: RecipePlan
    for plan in week.plans.all():
        plan.check_date()
        recipe = plan.recipe
        ingredients = recipe.ingredients.all()

        ing: RecipeIngredient
        for ing in ingredients:
            ing_name = ing.ingredient.title

            if not ing.ingredient.need_buy:  # Skip not required to buy ingredients
                continue

            if ing_name not in res:  # Create default ingredient
                res[ing_name] = get_default_ing()
                res[ing_name]["ingredient"] = ing.ingredient

            # -- Add ingredient amount
            res[ing_name]["amounts"].append([ing.amount_type, ing.amount])
            res[ing_name]["ingredients"].append(ing)

            # -- Update ingredient min_day
            if plan.day < res[ing_name]["min_day"]:
                res[ing_name]["min_day"] = plan.day

    # Add regular ingredients
    for regular_ing in RegularIngredient.objects.all():
        ing_name = regular_ing.ingredient.title
        if ing_name not in res:  # Create default ingredient
            res[ing_name] = get_default_ing()
            res[ing_name]["ingredient"] = regular_ing.ingredient

        res[ing_name]["amounts"].append([regular_ing.amount_type, regular_ing.amount])
        if regular_ing.day and regular_ing.day < res[ing_name]["min_day"]:
            res[ing_name]["min_day"] = regular_ing.day

    return res


def get_plan_week_ingredients(week: RecipePlanWeek) -> dict:
    """Get summarized list of products for week"""

    ingredients = get_week_ingredients(week)

    # // Analyze amounts

    for ing_name, info in ingredients.items():
        # List of unique measuring types of ingredient
        ing = info["ingredient"]
        amounts = info["amounts"]
        meas_types = list({measuring for measuring, amount in amounts})
        all_convert = all([is_convertible(m) for m in meas_types])
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
                "amount_type_str": amount_str(ing.amount_type),
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

    for ing_name, ing_info in ingredients.items():
        # ing: RecipeIngredient = ing_info["ingredient"]

        plan_item: ProductListItem
        amounts = get_ingredients_amounts(ing_info["ingredients"])

        plan_item, _ = plan_week.items.update_or_create(
            ingredient=ing_info["ingredient"],
            is_auto=True,
            defaults={
                "title": ing_name,
                "amount": ing_info["amount"],
                "amounts": amounts,
                "amount_type": ing_info["measuring"],
                "day": ing_info["min_day"] - 1,
                "is_deleted": False,
            },
        )

        plan_item.ingredients.set(ing_info["ingredients"])
        plan_item.save()
        edited_plans.append(plan_item.id)

    old_items = plan_week.items.filter(is_auto=True).exclude(id__in=edited_plans)
    # old_items.update(is_deleted=True)
    old_items.delete()

    return ingredients
