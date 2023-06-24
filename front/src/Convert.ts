import {
  Ingredient,
  IngredientRead,
  ProductListItem,
  ProductListItemRead,
  ProductListWeek,
  ProductListWeekRead,
  Recipe,
  RecipeIngredient,
  RecipePlan,
  RecipePlanWeek,
  RecipePlanWeekRead,
  RecipeRating,
  RecipeRead,
} from "src/client";

export function RecipePlanWeekFromRead(
  source: RecipePlanWeekRead | null
): RecipePlanWeek {
  const payloadReplaces = {
    plans: [] as RecipePlan[],
  };

  payloadReplaces.plans =
    source?.plans.map((p) => {
      const replaces = {
        recipe: undefined as number | undefined,
        meal_time: undefined as number | undefined,
      };
      if (typeof p.recipe == "object") {
        replaces.recipe = p.recipe?.id;
      }
      if (typeof p.meal_time == "object") {
        replaces.meal_time = p.meal_time.id;
      }
      return Object.assign({}, p, replaces) as RecipePlan;
    }) || [];

  // Exclude empty plans
  payloadReplaces.plans = payloadReplaces.plans.filter((p) => {
    return p.recipe && p.meal_time;
  });

  return Object.assign({}, source, payloadReplaces);
}

export function RecipeFromRead(source: RecipeRead | null): Recipe {
  const payloadReplaces = {
    images: source?.images || [],
    ingredients: [] as RecipeIngredient[],
    ratings: [] as RecipeRating[],
    recommendations_recipes: [] as number[],
  }

  payloadReplaces.ratings =
    source?.ratings?.map((r) => {
      const rep = { user: null as number | null }
      if (r.user?.id) {
        rep.user = r.user.id
      }
      return Object.assign({}, r, rep)
    }) || []

  payloadReplaces.ingredients =
    source?.ingredients?.map((r) => {
      const rep = {
        ingredient: r.ingredient.id,
      }
      return Object.assign({}, r, rep)
    }) || []

  payloadReplaces.recommendations_recipes =
    source?.recommendations_recipes?.map((r) => {
      return r.id
    }) || []

  return Object.assign({}, source, payloadReplaces);
}

export function productListItemFromRead(
  source: ProductListItemRead | null
): ProductListItem {
  const payloadReplaces = {
    ingredients: null,
    ingredient: source?.ingredient?.id || null,
  };

  return Object.assign({}, source, payloadReplaces);
}

export function productListWeekFromRead(
  source: ProductListWeekRead | null
): ProductListWeek {
  const payloadReplaces = {
    items: source?.items.map((i) => productListItemFromRead(i)),
  };
  return Object.assign({}, source, payloadReplaces);
}

export function ingredientFromRead(source: IngredientRead | null): Ingredient {
  const payloadReplaces = {
    // category: source?.category?.id,
  };
  return Object.assign({}, source, payloadReplaces);
}
