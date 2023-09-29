from dataclasses import dataclass
import logging
import random
from typing import TypeAlias
from recipes.models import MealTime, Recipe, RecipePlan, RecipePlanWeek, RecipeTag
from recipes.services.utils import get_random_obj_from_queryset

Day: TypeAlias = int


@dataclass
class RecipeTagConstraint:
    tag: RecipeTag
    count: int = 1


@dataclass
class PlanFillParams:
    recipes: list[Recipe] | None = None
    tag_constraints: list[RecipeTagConstraint] | None = None
    days: list[Day] | None = None


@dataclass
class RecipePreferences:
    day: list[Day] | None = None
    meal_time: list[MealTime] | None = None


# @dataclass
# class PlansGrid:
#     recipes: dict[Day, dict[MealTime, Recipe | None]]
#     total_count: int = 0

#     def set(self, day: Day, meal_time: MealTime, recipe: Recipe | None = None):
#         self.recipes[day][meal_time] = recipe


@dataclass
class PlanSlot:
    day: Day
    meal_time: MealTime


class PlanFill:
    params: PlanFillParams = PlanFillParams()
    # grid: PlansGrid
    week: RecipePlanWeek
    log = logging.getLogger("PlanFill")

    def __init__(self, week: RecipePlanWeek, params: PlanFillParams | None = None) -> None:
        if params is not None:
            self.params = params

        self.week = week
        # self.grid = self.get_empty_grid()

    @staticmethod
    def get_required_meal_times() -> list[MealTime]:
        """Get all required meal times"""
        return list(MealTime.objects.filter(is_primary=True).all())

    def set_recipe(self, day: Day, meal_time: MealTime, recipe: Recipe):
        """Set plan week recipe slot"""
        plan_item, is_created = self.week.plans.get_or_create(day=day, meal_time=meal_time, defaults={"recipe": recipe})
        self.log.debug(f"Set recipe (created: {is_created}): {day=}, {meal_time=}, {recipe=}")
        return plan_item

    def set_recipe_slot(self, slot: PlanSlot, recipe: Recipe):
        """Set plan week recipe by slot"""
        self.set_recipe(slot.day, slot.meal_time, recipe)

    def get_recipe(self, day: Day, meal_time: MealTime) -> RecipePlan | None:
        """Get recipe plan by params"""
        try:
            res = self.week.plans.get(day=day, meal_time=meal_time)
        except RecipePlanWeek.DoesNotExist:
            return None
        else:
            return res

    @property
    def plan_days(self):
        if not self.params.days:
            return list(range(1, 7 + 1))
        return self.params.days

    def get_all_slots(self) -> list[PlanSlot]:
        """Get all existing slots"""
        slots: list[PlanSlot] = []
        for day in self.plan_days:
            for meal_time in self.get_required_meal_times():
                slots.append(PlanSlot(day=day, meal_time=meal_time))

        return slots

    def get_empty_slots(self) -> list[PlanSlot]:
        """Get all empty plan slots"""
        slots = self.get_all_slots()

        for plan in self.week.plans.all():
            slot = PlanSlot(day=plan.day, meal_time=plan.meal_time)
            if slot in slots:
                slots.remove(slot)

        self.log.debug(f"Empty slots ({len(slots)}): {slots}")
        return slots

    def get_all_used_recipes(self):
        """Get list of used recipes IDS"""
        return self.week.plans.values_list("recipe", flat=True).distinct()

    # def plan_save(self):
    #     self.week.save(update_fields=["plans"])

    ###

    def get_recipe_preferences(self, recipe: Recipe) -> RecipePreferences:
        """Get recipe placement preferences"""
        prefs = RecipePreferences()
        meal_times = self.get_required_meal_times()
        meal_times_str = {m.title.lower(): m for m in meal_times}

        # Preferred meal times
        for tag in recipe.tags.all():
            if tag.title.lower() in meal_times_str:
                if prefs.meal_time is None:
                    prefs.meal_time = []
                prefs.meal_time.append(meal_times_str[tag.title.lower()])

        return prefs

    def get_random_slot(self):
        empty_slots = self.get_empty_slots()
        assert len(empty_slots) > 0
        return random.choice(empty_slots)

    def get_recipe_auto_slot(self, recipe: Recipe):
        """Choice an empty plan slot for recipe"""
        prefs = self.get_recipe_preferences(recipe)
        self.log.debug(f"Auto placing recipe: {recipe}. Preferences: {prefs}")

        all_slots = self.get_empty_slots()
        ideal_slots = all_slots.copy()

        if prefs.meal_time:
            for slot in ideal_slots:
                if slot.meal_time not in prefs.meal_time:
                    ideal_slots.remove(slot)

        if prefs.day:
            for slot in ideal_slots:
                if slot.day not in prefs.day:
                    ideal_slots.remove(slot)
        # Auto preferences

        #

        if ideal_slots:
            res = random.choice(ideal_slots)
            self.log.debug(f"Ideal slots choice ({len(ideal_slots)}): {res}")
            return res

        return random.choice(all_slots)

    def auto_place_recipe(self, recipe: Recipe):
        """Automatically place recipe in week plan"""

        slot = self.get_recipe_auto_slot(recipe)
        return self.set_recipe_slot(slot, recipe)

    def get_tag_recipes_count(self, tag_id: int):
        return self.week.plans.filter(recipe__tags__in=[tag_id]).distinct().count()

    def get_recipe_by_tag(self, tag: RecipeTag):
        self.log.debug(f"Placing recipe by tag: {tag}")

        qs = Recipe.objects.filter(tags__in=[tag])
        recipe = get_random_obj_from_queryset(qs)
        return recipe

    def execute_constraints(self):
        """Auto create recipes for constraints"""

        # -- Tag constraint
        if self.params.tag_constraints:
            for tag_constraint in self.params.tag_constraints:
                current_count = self.get_tag_recipes_count(tag_constraint.tag.pk)
                target_count = tag_constraint.count

                self.log.debug(f"Tag constraint: {current_count}/{target_count} {tag_constraint.tag}")
                if target_count > current_count:
                    for _ in range(target_count - current_count):
                        recipe = self.get_recipe_by_tag(tag_constraint.tag)
                        self.auto_place_recipe(recipe)

    ###

    def empty_plan(self):
        for p in self.week.plans.all():
            p.delete()

    def supply_plan(self):
        """Supply not full plan with recipes"""
        raise NotImplementedError()

    def auto_arrange_recipes(self):
        """Auto arrange recipes to plan"""

        used_recipes = self.get_all_used_recipes()
        self.log.debug(f"Used recipes: {used_recipes}")

        if self.params.recipes is not None:
            for recipe in self.params.recipes:
                if recipe.pk in used_recipes:
                    self.log.debug(f"Skipped used recipe: {recipe}.")
                    continue

                self.auto_place_recipe(recipe)

        self.execute_constraints()

    def auto_fill(self):
        """Completely auto fill plan"""
        raise NotImplementedError()
