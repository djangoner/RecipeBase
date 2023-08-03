from dataclasses import dataclass
from recipes.models import Ingredient
from fuzzywuzzy import process
from cachetools.func import ttl_cache


@dataclass
class IngredientMatch:
    ingredient: Ingredient
    score: float | None = None
    full: bool = False


@ttl_cache(1, 60)
def get_all_ingredients() -> list[str]:
    return Ingredient.objects.all().values_list("title", flat=True)


@ttl_cache(128, 10)
def get_ingredient_by_name(name: str) -> Ingredient | None:
    return Ingredient.objects.get(title=name)


def search_ingredient(name: str, min_score: int = 70) -> list[IngredientMatch] | None:
    all_ings: list[str] = get_all_ingredients()
    res = []

    matches = process.extractBests(name, all_ings, score_cutoff=min_score, limit=5)
    for match in matches:
        if match and len(match) == 2:
            best_value: str
            best_score: float
            (best_value, best_score) = match

            ingredient = get_ingredient_by_name(best_value)
            is_full = best_value == 100 or best_value.lower() == name.lower()

            res.append(IngredientMatch(ingredient=ingredient, full=is_full, score=best_score))

    return res
