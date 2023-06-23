from dataclasses import dataclass, field
import logging
from typing import Optional
from recipes.models import (
    MealTime,
    Recipe,
    RecipeIngredientRecommendation,
    RecipePlan,
    RecipePlanWeek,
    RecipeTag,
)
from rest_framework import exceptions
from constance import config


@dataclass(unsafe_hash=True, eq=True)
class Recommendation:

    idx: Optional[int] = None
    hash: Optional[str] = field(init=False, compare=False, hash=False)
    recipe: Optional[Recipe] = None
    recipe_tag: Optional[RecipeTag] = None
    ingredient: Optional[RecipeIngredientRecommendation] = None
    plan: Optional[RecipePlan] = None
    description: Optional[str] = None


@dataclass(frozen=True, eq=True)
class RecommendationHashable:
    idx: Optional[int] = None
    recipe: Optional[int] = None
    recipe_tag: Optional[int] = None
    ingredient: Optional[int] = None
    plan: Optional[int] = None

    @classmethod
    def from_recommendation(cls, recommendation: Recommendation):
        opts = {}
        for k, v in recommendation.__dict__.items():
            if not hasattr(cls, k):  # Skip unsupported
                continue
            if hasattr(v, "pk"):  # Get PK value from DB object
                v = getattr(v, "pk")
            opts[k] = v
        return cls(**opts)


def gen_recommendation_hash(rec: Recommendation):
    hashable = RecommendationHashable.from_recommendation(rec)
    return hash(hashable)


def get_plan_recommended(plan: RecipePlan) -> list[Recommendation]:
    res: list[Recommendation] = []
    recipe = plan.recipe
    assert recipe is not None, "recipe must not be None"

    if recipe.recommendations_recipes.count():
        for rec_recipe in recipe.recommendations_recipes.all():
            res.append(
                Recommendation(
                    recipe=rec_recipe,
                    plan=plan,
                )
            )
    if recipe.recommendations_tags.count():
        for rec_tag in recipe.recommendations_tags.all():
            res.append(
                Recommendation(
                    recipe_tag=rec_tag,
                    plan=plan,
                )
            )
    if recipe.recommendations_ingredients.count():
        for recommendation_ing in recipe.recommendations_ingredients.all():
            res.append(
                Recommendation(
                    ingredient=recommendation_ing,
                    plan=plan,
                )
            )

    return res


def get_week_recipes_recommendations(plan: RecipePlanWeek) -> list[Recommendation]:
    res: list[Recommendation] = []

    for plan_item in plan.plans.all():
        res.extend(get_plan_recommended(plan_item))

    return res


def generate_recommendations(plan: RecipePlanWeek) -> list[Recommendation]:
    res: list[Recommendation] = []

    res.extend(get_week_recipes_recommendations(plan))

    ## Process and return
    for i in range(len(res)):
        # res[i].idx = i
        res[i].hash = str(gen_recommendation_hash(res[i]))

    return res


def find_recommendation(plan: RecipePlanWeek, hash_val: int):
    recs = generate_recommendations(plan)
    for rec in recs:
        if rec.hash == hash_val:
            return rec


def accept_recommendation_recipe(plan: RecipePlanWeek, recommendation: Recommendation, remove_old: bool = False):
    assert recommendation.recipe is not None
    assert recommendation.plan is not None

    meal_time_id: int = config.RECOMMENDATION_MEAL_TIME  # noqa
    meal_time = MealTime.objects.filter(id=meal_time_id).first()
    if not meal_time:
        logging.warning("Recommendation default meal time not found")
        return False

    RecipePlan.objects.create(week=plan, day=recommendation.plan.day, meal_time=meal_time, recipe=recommendation.recipe)
    return True


def accept_recommendation_ingredient(plan: RecipePlanWeek, recommendation: Recommendation):
    pass


def accept_recommendation(plan: RecipePlanWeek, recommendation: Recommendation) -> bool | None:
    logging.info("Acception recommendation...")
    if recommendation.recipe:
        return accept_recommendation_recipe(plan, recommendation)
    elif recommendation.ingredient:
        return accept_recommendation_ingredient(plan, recommendation)
    elif recommendation.recipe_tag:
        raise exceptions.APIException("Can't accept recipe tag", "cant_accept")
