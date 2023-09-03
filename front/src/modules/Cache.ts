import { RecipeRead, RecipeShort } from "src/client"
import { useBaseStore } from "src/stores/base"
import { useCacheStore } from "src/stores/cache"

interface LoadCachedRecipeParams {
  omit?: string
}

export function extractRecipeId(recipe: number | RecipeShort) {
  if (typeof recipe === "number") {
    return recipe
  }
  return recipe.id
}

export function cacheKeyRecipe(short: number | RecipeShort | RecipeRead) {
  return { recipe: extractRecipeId(short) }
}

export function getCachedRecipe<T extends number | RecipeShort>(short: T): RecipeRead | T {
  const cacheKey = cacheKeyRecipe(short)
  const storeCache = useCacheStore()
  const cachedRecipe = storeCache.getCached(cacheKey) as undefined | RecipeRead
  // console.debug("Check cached: ", cacheKey, cachedRecipe)
  if (cachedRecipe) {
    return cachedRecipe
  }

  return short
}

export function loadCachedRecipe(id: number | RecipeShort, params: LoadCachedRecipeParams = {}): Promise<RecipeRead> {
  // console.debug("Loading for cache...", id)
  const store = useBaseStore()
  const storeCache = useCacheStore()
  const cacheKey = cacheKeyRecipe(id)
  if (storeCache.getCached(cacheKey)) {
    const prom: Promise<RecipeRead> = new Promise((resolve) => resolve(storeCache.getCached(cacheKey) as RecipeRead))
    return prom
  }
  const omit = "content,content_source,recommendations_ingredients,recommendations_recipes,recommendations_tags"
  const prom = store.loadRecipe(extractRecipeId(id), params.omit || omit)
  void prom.then((data) => {
    storeCache.setCached(cacheKey, data)
    // console.debug("Caching recipe #" + props.recipe.id.toString())
  })
  return prom
}
