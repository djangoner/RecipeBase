from dataclasses import dataclass, field
from datetime import datetime
import itertools
import logging
from typing import Optional, TypeAlias
from recipes.models import Recipe, RecipePlan, RecipePlanWeek, RecipeRating, WeekPlanCondition
from users.models import UserProfile
from django.contrib.auth.models import AbstractBaseUser
from cachetools.func import ttl_cache

log = logging.getLogger("Conditions")

ConditionType: TypeAlias = int | str
ConditionValue: TypeAlias = int | str | None
CACHE_TTL = 5


@dataclass
class ConditionWarning:
    condition: WeekPlanCondition
    value_current: ConditionValue
    value_expected: ConditionValue
    plan: Optional[RecipePlan] = None
    childrens: list["ConditionWarning"] = field(default_factory=list)


@dataclass
class ConditionsResult:
    warnings: list[ConditionWarning]


# def build_condition_text(cond: WeekPlanCondition):
#     pass


def warnings_json(warnings: list[ConditionWarning]):
    res: list[dict] = []
    for w in warnings:
        assert w.plan is not None
        res.append(
            {
                "value_current": w.value_current,
                "value_expected": w.value_expected,
                "condition": w.condition.pk,
                "plan": w.plan.pk,
                "childrens": warnings_json(w.childrens),
            }
        )
    return res


def get_selector_value(cond: WeekPlanCondition) -> ConditionType | None:
    """Get second condition value, usually static."""
    if cond.selector_type == WeekPlanCondition.SelectorType.WEEKDAY:
        now = datetime.now()
        return now.isoweekday()

    # assert cond.selector_value is not None
    # return cond.selector_value


def try_int(value) -> int | str:
    """Try converting to int or do nothing"""
    if isinstance(value, str) and value.isdigit():
        return int(value)

    return value


@ttl_cache(4, ttl=CACHE_TTL)
def get_week_plans(week: RecipePlanWeek):
    """Return recipe plan week plans list"""
    return week.plans.all()


@ttl_cache(32, ttl=CACHE_TTL)
def get_condition_childrens(cond: WeekPlanCondition):
    return cond.childrens.all()


@ttl_cache(32, ttl=CACHE_TTL)
def get_recipe_tags(recipe: Recipe):
    return recipe.tags.all()


@ttl_cache(32, ttl=CACHE_TTL)
def get_recipe_ratings(recipe: Recipe):
    return recipe.ratings.all()


@ttl_cache(32, ttl=CACHE_TTL)
def get_week_tag(week: RecipePlanWeek, tag_id: int, plan: Optional[RecipePlan] = None) -> tuple[int, bool]:
    """Counts the number of tags with given ID in week"""
    res = 0
    plan_contains = False

    for p in get_week_plans(week):
        recipe = p.recipe
        assert recipe is not None

        for t in get_recipe_tags(recipe):
            if t.pk == tag_id:
                res += 1
                if plan and p.pk == plan.pk:
                    plan_contains = True

    return (res, plan_contains)


def recipe_contains_tag(recipe: Recipe, tag_id: int) -> bool:
    """Is recipe contains tag with given ID"""
    for t in recipe.tags.all():
        if t.pk == tag_id:
            return True
    return False


def recipe_contains_ingredient(recipe: Recipe, ing_id: int, is_main: bool | None = None) -> bool:
    """Is recipe contains ingredient with given ID, filtering by is_main is optional."""

    for ing in recipe.ingredients.all():
        if is_main is not None and is_main != ing.is_main:
            continue

        if ing.pk == ing_id:
            return True

    return False


def plan_is_meal_time(plan: RecipePlan, mtime_id: int) -> bool:
    """Is plan meal time ID equals to given ID"""
    return plan.meal_time.pk == mtime_id


@ttl_cache(32, ttl=CACHE_TTL)
def get_user_profile(user: AbstractBaseUser) -> UserProfile:
    """Get user profile for user instance"""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@ttl_cache(32, ttl=CACHE_TTL)
def get_week_all_plans_by_day(week: RecipePlanWeek, day_num: int) -> list[RecipePlan]:
    """Get all week plans for given day number"""
    r: list[RecipePlan] = []
    for plan in get_week_plans(week):
        if plan.day != day_num:
            continue
        r.append(plan)
    return r


@ttl_cache(32, ttl=CACHE_TTL)
def get_plan_day_ratings(plan: RecipePlan, filter_user: Optional[int] = None) -> list[int]:
    """Get ratings list for plan day"""
    ratings: list[RecipeRating] = []

    assert plan.day is not None
    for p in get_week_all_plans_by_day(plan.week, plan.day):
        assert p.recipe is not None
        for r in get_recipe_ratings(p.recipe):
            if filter_user:  # If filtered or included in conditions
                if not r.user.pk == filter_user:
                    continue
            else:
                if not get_user_profile(r.user).conditions_include:
                    continue
            ratings.append(r)

    ratings_num = [r.rating for r in ratings]
    return ratings_num


def get_week_duplicates(plan: RecipePlan) -> int:
    r = 0
    for p in get_week_plans(plan.week):
        assert plan.recipe is not None and p.recipe is not None

        if p.recipe.pk == plan.recipe.pk:
            r += 1

    return r


@ttl_cache(32, ttl=CACHE_TTL)
def get_plan_value(cond: WeekPlanCondition, plan: RecipePlan):
    """Get first condition value based on week plan."""
    field = cond.plan_field
    assert plan.recipe is not None

    if field == WeekPlanCondition.Field.WEEKDAY:
        return plan.day

    elif field == WeekPlanCondition.Field.INGREDIENT:
        assert cond.selector_value is not None
        ing_id = int(cond.selector_value)
        return int(recipe_contains_ingredient(plan.recipe, ing_id))

    elif field == WeekPlanCondition.Field.INGREDIENT_MAIN:
        assert cond.selector_value is not None
        ing_id = int(cond.selector_value)
        return int(recipe_contains_ingredient(plan.recipe, ing_id))

    elif field == WeekPlanCondition.Field.TAG:
        assert cond.selector_value is not None
        tag_id = int(cond.selector_value)
        return int(recipe_contains_tag(plan.recipe, tag_id))

    elif field in [WeekPlanCondition.Field.TAG_WEEK]:
        assert cond.selector_value is not None
        res, contains = get_week_tag(plan.week, int(cond.selector_value), plan=plan)
        if not contains:
            return 0
        return res

    elif field == WeekPlanCondition.Field.MEAL_TIME:
        return plan.meal_time.pk

    elif field == WeekPlanCondition.Field.COOKING_TIME:
        return plan.recipe.cooking_time

    elif field in [WeekPlanCondition.Field.MIN_RATING, WeekPlanCondition.Field.MAX_RATING]:
        filter_user = None
        if cond.selector_value and cond.selector_value.isdigit():
            filter_user = int(cond.selector_value)

        ratings = get_plan_day_ratings(plan, filter_user=filter_user)
        if not ratings:
            return 0

        if field == WeekPlanCondition.Field.MIN_RATING:
            return min(ratings) if ratings else 0
        elif field == WeekPlanCondition.Field.MAX_RATING:
            return max(ratings) if ratings else 0

    elif field == WeekPlanCondition.Field.DUPLICATES:
        return get_week_duplicates(plan)

    # Unknown error
    else:
        raise NotImplementedError(f"Field processing for '{field}' is not implemented")


def is_num(value: int | str | None) -> bool:
    if isinstance(value, int):
        return True
    elif isinstance(value, str):
        return value.isdigit()

    return False


def compare_condition_values(cond: WeekPlanCondition, value_current, value_expected) -> bool | None:
    mode = cond.comparison_mode or WeekPlanCondition.ComparisonMode.EQUAL
    is_numbers = is_num(value_current) and is_num(value_expected)

    if mode == WeekPlanCondition.ComparisonMode.EQUAL:
        return value_expected == value_current or str(value_expected) == str(value_current)
    elif mode == WeekPlanCondition.ComparisonMode.NOT_EQUAL:
        return value_expected != value_current
    elif is_numbers and mode == WeekPlanCondition.ComparisonMode.GT:
        return int(value_current) > int(value_expected)
    elif is_numbers and mode == WeekPlanCondition.ComparisonMode.GE:
        return int(value_current) >= int(value_expected)
    elif is_numbers and mode == WeekPlanCondition.ComparisonMode.LT:
        return int(value_current) < int(value_expected)
    elif is_numbers and mode == WeekPlanCondition.ComparisonMode.LE:
        return int(value_current) <= int(value_expected)

    return False


def process_children_values(cond: WeekPlanCondition, values: list[list[ConditionWarning]]) -> bool:
    condition = cond.condition
    childrens_values = [len(c) > 0 for c in values]

    if condition == WeekPlanCondition.Condition.AND:
        return all(childrens_values)
    elif condition == WeekPlanCondition.Condition.OR:
        return any(childrens_values)
    elif condition == WeekPlanCondition.Condition.NOT:
        return not (any(childrens_values))

    return False


def process_condition(cond: WeekPlanCondition, plan: RecipePlan):
    """Process condition, also process childrens tree if required."""

    warnings: list[ConditionWarning] = []
    # log.info(f"Processing condition {cond} with ({plan})")

    ## -- Nested
    childrens = get_condition_childrens(cond)
    if childrens:
        # log.debug("Processing nested conditions...")
        children_values: list[list[ConditionWarning]] = []
        for c in childrens:
            children_values.append(process_condition(c, plan))

        res = process_children_values(cond, children_values)
        if res:
            warnings.append(
                ConditionWarning(
                    cond, "1", "1", plan=plan, childrens=list(itertools.chain.from_iterable(children_values))
                )
            )

        # log.debug(f"Children res: {res}")
        # log.debug(f"Children values (condition: {cond.condition}): '{[len(c) for c in children_values]}'")
        return warnings
    ##

    value_current = try_int(get_plan_value(cond, plan))
    # log.debug(f"Extracted plan value ({cond.plan_field}): {value_current}")
    # value_expected = get_selector_value(cond)
    selector_item = try_int(get_selector_value(cond))
    # log.debug(f"Extracted selector item ({cond.selector_type}): {selector_item}")
    manual_value = try_int(cond.manual_value)

    if selector_item:
        value_expected = selector_item
    else:
        value_expected = manual_value

    is_matching = compare_condition_values(cond, value_current, value_expected)

    if is_matching:
        warnings.append(ConditionWarning(cond, value_current, value_expected, plan=plan))

    return warnings


def process_conditions_tree(week: RecipePlanWeek):
    """Process conditions tree"""

    # Process only root active conditions
    root_conditions = WeekPlanCondition.objects.filter(parent__isnull=True, active=True)
    warnings: list[ConditionWarning] = []
    # log.info(f"Checking conditions {root_conditions}...")

    for plan in week.plans.all():
        for cond in root_conditions:
            cond_warnings = process_condition(cond, plan)
            if cond_warnings:
                warnings.extend(cond_warnings)

    return ConditionsResult(warnings=warnings)
