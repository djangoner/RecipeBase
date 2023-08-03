from dataclasses import dataclass
import logging
import math
import re
from typing import Tuple
from recipes.models import Ingredient, ProductListItem
from recipes.services.measurings import (
    convert_all_to_grams,
    translate_measuring,
)
from recipes.models import RecipeIngredient, RegularIngredient
from lxml import html, etree
from recipes.services.utils import first_or_none

from telegram_bot.services.search import search_ingredient

log = logging.getLogger(__name__)


@dataclass
class RecognizedIngredient:
    ingredient: Ingredient
    amount: int
    amount_type: str = "g"


def extract_ingredient_amount(ing: RecipeIngredient | RegularIngredient):
    if (
        ing.amount_type == "items" and ing.ingredient.item_weight and ing.ingredient.type != "item"
    ):  # Convert items to grams
        return ("g", int(ing.amount * ing.ingredient.item_weight))
    elif (
        ing.amount_type == "items" and ing.ingredient.min_pack_size and ing.ingredient.type != "item"
    ):  # Fallback to min_pack_size if items and no item size
        return ("g", int(ing.amount * ing.ingredient.min_pack_size))
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
        return recipe_ingredient_price_full(ing)
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


def ingredients_html_extractor(text: str) -> list[str] | None:
    try:
        tree = html.fromstring(text)
    except Exception as e:
        log.warning("HTML parsing error", exc_info=e)
        return None
    tags = tree.xpath("//li")
    if not tags:
        return None

    res = []
    for tag in tags:
        if not tag.text:
            continue
        res.append(tag.text)

    log.info(f"Extracted HTML items :\n{res}")
    return res


def text_html_format(text: str):
    try:
        tree = html.fromstring(text)
    except Exception as e:
        log.warning("HTML parsing error", exc_info=e)
        return text
    return etree.tostring(tree, pretty_print=True, encoding="unicode")


def words_measuring(line: str):
    normalized = re.sub(r"[\d\W]", " ", line).lower().strip()
    words = normalized.split(" ")
    for word in words:
        if translated := translate_measuring(word.lower().strip()):
            return word, translated


def ingredients_text_extractor(text: str) -> list[str] | None:
    res = []
    text = text.replace("–", "-")
    text = re.sub(r"<[^>]*>", " ", text).lower().strip()  # Remove HTML

    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    log.debug(f"Cleared text:\n{text}")

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            pass
        elif "-" in line:
            pass
        elif word_res := words_measuring(line):
            word_found, word_translated = word_res
            re_match = re.search(r"\d", line)

            insert_index: int = 0

            if re_match:
                insert_index = re_match.start()
            else:
                insert_index = line.index(word_found)

            if insert_index:
                line = line[:insert_index] + "-" + line[insert_index:]

        else:
            continue

        res.append(line)

    return res


def line_split_ingredient(line: str) -> Tuple[str, str] | None:
    """Split line in ingredient and amount parts"""
    spl = line.split("-")

    if "-" in line and len(spl) >= 2:
        return (spl[0].strip(), spl[1].strip())

    numbers_match = re.search(r"[\d.]+", line)

    if numbers_match:
        index = numbers_match.pos
        return (line[:index].strip(), line[index:].strip())

    return None


def extract_amount_type(line: str):
    normalized = re.sub(r"[\d\W]", " ", line).lower().strip()

    for word in normalized.split(" "):
        if not word:
            continue
        word = word.strip()

        if translated := translate_measuring(word):
            return translated

    log.info(f"Not found amount type: '{normalized}'")


def process_ingredients(items: list[str]) -> list[RecognizedIngredient] | None:
    """Process ingredients list to recipe ingredients"""
    res: list[RecognizedIngredient] = []
    log.info(f"Extracted items:\n{items}")
    # print("Items: ", items)
    for line in items:
        words = line.split(" ")
        if len(line) > 100:
            continue
        elif len(words) < 2 or len(words) > 10:
            continue

        line_split = line_split_ingredient(line)
        if not line_split:
            continue

        ingredient_name, amount_raw = line_split
        ingredient = first_or_none(search_ingredient(ingredient_name, min_score=80))
        amount_type = extract_amount_type(amount_raw)

        if not ingredient:
            log.info(f"Not found ingredient for: '{ingredient_name}'")
            continue

        amount_re = re.search(r"\d+", amount_raw)
        amount_number = 0
        if amount_re:
            amount_number = int(amount_re.group(0))

        res.append(
            RecognizedIngredient(
                ingredient=ingredient.ingredient,
                amount=amount_number,
                amount_type=amount_type or "g",  # Fill
            )
        )

        # print("Item: ", line_split, ingredient)
    return res or None


def recognize_ingredients_text(text: str, text_only: bool = True) -> list[RecognizedIngredient] | None:
    """Recognize text with ingredients and return recipe ingredients list"""

    ## Prepare ingredients lines
    items = None
    log.info("Recognizing ingredients text...")

    # if not text_only:
    #     items = ingredients_html_extractor(text)
    if not items or text_only:
        log.info("HTML extractor failed, trying text extractor...")
        text = text_html_format(text)
        items = ingredients_text_extractor(text)

    if not items:
        log.info("No ingredients found")
        return None

    ## Process ingredients lines
    return process_ingredients(items)
