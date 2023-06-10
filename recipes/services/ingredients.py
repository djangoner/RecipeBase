import math
from recipes.models import ProductListItem
from recipes.services.measurings import convert_all_to_grams
from recipes.models import RecipeIngredient, RegularIngredient


def extract_ingredient_amount(ing: RecipeIngredient | RegularIngredient):
    if (
        ing.amount_type == "items" and ing.ingredient.item_weight and ing.ingredient.type != "item"
    ):  # Convert items to grams
        return ("g", int(ing.amount * ing.ingredient.item_weight))
    else:
        return (ing.amount_type, ing.amount)


def recipe_ingredient_packs(ing: ProductListItem | RecipeIngredient) -> float:
    if not (ing.amount and ing.ingredient and ing.ingredient.min_pack_size):
        return 0

    meas_extracted = extract_ingredient_amount(ing)
    amount = meas_extracted[1]
    if ing.amount_type not in ["items"]:
        _, amount = convert_all_to_grams([meas_extracted])
    return round(amount / ing.ingredient.min_pack_size, 3)


def recipe_ingredient_price_part(ing: ProductListItem | RecipeIngredient) -> float | None:
    if not (
        ing.ingredient
        and (ing.ingredient.min_pack_size or ing.ingredient.item_weight)
        and ing.ingredient.price
        and ing.amount
    ):
        return None
    packs = recipe_ingredient_packs(ing)
    return round(packs * ing.ingredient.price)


def recipe_ingredient_price_full(ing: ProductListItem | RecipeIngredient):
    if not (
        ing.ingredient
        and (ing.ingredient.min_pack_size or ing.ingredient.item_weight)
        and ing.ingredient.price
        and ing.amount
    ):
        return

    packs = math.ceil(recipe_ingredient_packs(ing))
    return round(packs * ing.ingredient.price)
