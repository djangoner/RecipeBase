import math
from recipes.models import ProductListItem, RecipeIngredient
from recipes.services.measurings import convert_all_to_grams


def recipe_ingredient_packs(ing: ProductListItem | RecipeIngredient) -> float:
    if not (ing.amount and ing.ingredient and ing.ingredient.min_pack_size):
        return 0

    meas, amount = convert_all_to_grams([(ing.amount_type or "g", ing.amount)])
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
    if ing.ingredient.type == "item" and ing.ingredient.min_pack_size:
        return round(ing.amount / ing.ingredient.min_pack_size * ing.ingredient.price)
    elif ing.amount_type == "items" and ing.ingredient.item_weight and ing.ingredient.min_pack_size:
        return round(packs * ing.ingredient.item_weight / ing.ingredient.min_pack_size)
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
    if (
        ing.amount_type == "items"
        and ing.ingredient.item_weight
        and ing.ingredient.min_pack_size
        and not ing.ingredient.type == "item"
    ):
        return round(ing.amount * ing.ingredient.item_weight / ing.ingredient.min_pack_size * ing.ingredient.price)
    return round(packs * ing.ingredient.price)
