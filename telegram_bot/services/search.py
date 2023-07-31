from dataclasses import dataclass
from recipes.models import Ingredient
from fuzzywuzzy import process


@dataclass
class IngredientMatch:
    ingredient: Ingredient
    score: float | None = None
    full: bool = False


def search_ingredient(name: str, min_score: int = 70) -> list[IngredientMatch] | None:
    all_ings: list[str] = Ingredient.objects.all().values_list("title", flat=True)
    res = []

    matches = process.extractBests(name, all_ings, score_cutoff=min_score, limit=5)
    for match in matches:
        if match and len(match) == 2:
            best_value: str
            best_score: float
            (best_value, best_score) = match

            ingredient = Ingredient.objects.get(title=best_value)
            is_full = best_value == 100 or best_value.lower() == name.lower()

            res.append(IngredientMatch(ingredient=ingredient, full=is_full, score=best_score))

    return res
