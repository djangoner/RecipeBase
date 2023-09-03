from recipes.models import ProductListItem, ProductListWeek, RecipePlanWeek
from recipes.services.ingredients import recipe_ingredient_price_full
from recipes.services.plans import get_plan_week_ingredients
from users.models import UserProfile


def get_week_price(week: RecipePlanWeek) -> float:
    """Get total price of week ingredients"""
    res = 0.0
    ingredients = get_plan_week_ingredients(week)

    product_week = ProductListWeek(year=week.year, week=week.week)

    for ing_name, ing in ingredients.items():
        product_item = ProductListItem(
            week=product_week,
            ingredient=ing.ingredient,
            amount=ing.amount,
            amount_type=ing.measuring,
            day=ing.min_day - 1,
        )
        ing_price = recipe_ingredient_price_full(product_item)
        if ing_price:
            res += ing_price

    return res


def get_week_stats(week: RecipePlanWeek):
    """Recipe week plan stats"""
    res = {"price_part": 0.0, "price_full": 0.0, "price": 0.0, "rating": {}}

    plans = week.plans.prefetch_related("recipe", "recipe__ratings").all()

    # Ratings template
    for u in UserProfile.objects.select_related("user").all():
        if u.user.is_active and u.show_rate:
            res["rating"][u.user.pk] = [-1 for _ in range(7)]

    res["price"] = get_week_price(week)
    for plan in plans:
        recipe = plan.recipe
        if not recipe:
            continue
        # Price
        res["price_part"] += recipe.price_part
        res["price_full"] += recipe.price_full
        # Ratings

        for rating in recipe.ratings.all():
            if rating.user.pk not in res["rating"]:
                continue

            user_ratings = res["rating"][rating.user.pk]
            val = user_ratings[plan.day - 1]
            if rating.rating > val:
                user_ratings[plan.day - 1] = rating.rating

    return res
