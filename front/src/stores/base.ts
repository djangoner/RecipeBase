import { defineStore } from "pinia"
import { LocalStorage, Notify } from "quasar"
import {
  AmountTypes,
  Ingredient,
  IngredientCategory,
  IngredientCategoryService,
  IngredientRead,
  IngredientsService,
  MealTime,
  MealTimeService,
  OpenAPI,
  PaginatedIngredientCategoryList,
  PaginatedIngredientReadList,
  PaginatedProductListItemReadList,
  PaginatedProductListWeekReadList,
  PaginatedRecipePlanWeekReadList,
  PaginatedRecipeReadList,
  PaginatedRecipeTagList,
  PaginatedTaskCategoryList,
  PaginatedTaskNestedList,
  PatchedRecipe,
  ProductListItem,
  ProductListItemRead,
  ProductListItemService,
  ProductListWeek,
  ProductListWeekRead,
  ProductListWeekService,
  Recipe,
  RecipeImage,
  RecipePlanWeek,
  RecipePlanWeekRead,
  RecipePlanWeekService,
  RecipeRead,
  RecipesService,
  RecipeTag,
  RecipeTagsService,
  Shop,
  ShopService,
  StatsList,
  StatsService,
  Task,
  TaskCategory,
  TaskCategoryService,
  TaskService,
  WeekPlanCondition,
  ConditionsService,
} from "src/client"
import { request } from "src/client/core/request"
import { productListItemFromRead } from "src/Convert"
import { CustomAxiosError, handleErrors } from "src/modules/HandleErrorsMixin"
import { getDB, ProductListItemSyncable, recipePlansGetOffline, recipePlansListUpdateFromServer } from "src/modules/ProductListSync"
import { mockedPaginatedResponse, objectUnproxy, onlyChangedFields } from "src/modules/SyncUtils"

const isOnline = () => navigator?.onLine

export const useBaseStore = defineStore("base", {
  state: () => ({
    printMode: false,

    stats: null as StatsList | null,
    recipes: null as RecipeRead[] | null,
    recipe: null as RecipeRead | null,
    tags: null as RecipeTag[] | null,
    amount_types: null as AmountTypes | null,
    week_plan: null as RecipePlanWeekRead | null,
    week_plans: null as RecipePlanWeekRead[] | null,
    meal_time: null as MealTime[] | null,
    product_list: null as ProductListWeekRead | null,
    product_lists: null as ProductListWeekRead[] | null,
    product_list_items: null as ProductListItemRead[] | null,
    product_list_item: null as ProductListItemRead | null,
    ingredients: null as IngredientRead[] | null,
    ingredients_searched: false,
    ingredient: null as IngredientRead | null,
    tasks: null as Task[] | null,
    task: null as Task | null,
    tasks_categories: null as TaskCategory[] | null,
    ingredient_categories: null as IngredientCategory[] | null,
    shops: null as Shop[] | null,
    conditions: null as WeekPlanCondition[] | null,
  }),

  getters: {
    appVersion(): string {
      return process.env.PACKAGE_VERSION || "0"
    },
  },

  actions: {
    // -- Essentials

    async loadStats(): Promise<StatsList> {
      return new Promise((resolve, reject) => {
        StatsService.statsList()
          .then((resp) => {
            const stat = resp[0] || resp
            this.stats = stat
            resolve(stat)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadAmountTypes(): Promise<AmountTypes> {
      if (!isOnline()) {
        const res: AmountTypes | null = LocalStorage.getItem("cached:amount_types")
        if (res) {
          this.amount_types = res
          return new Promise((resolve) => {
            resolve(this.amount_types as AmountTypes)
          })
        }
      }
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsAmountTypesRetrieve()
          .then((resp) => {
            this.amount_types = resp
            resolve(resp)
            LocalStorage.set("cached:amount_types", resp)
          })
          .catch((err) => {
            reject(err)
            const res: AmountTypes | null = LocalStorage.getItem("cached:amount_types")
            if (res) {
              this.amount_types = res
              return new Promise((resolve) => {
                resolve(this.amount_types as AmountTypes)
              })
            }
          })
      })
    },
    async loadMealTime(payload: object): Promise<MealTime[]> {
      const db = await getDB()

      if (!isOnline()) {
        const res = (await db.getAll("meal_time")) as MealTime[]
        this.meal_time = res
        return new Promise((resolve) => {
          resolve(this.meal_time as MealTime[])
        })
      }
      return new Promise((resolve, reject) => {
        MealTimeService.mealTimeList(payload)
          .then(async (resp) => {
            this.meal_time = resp.results as MealTime[]
            resolve(resp as MealTime[])
            for (const item of resp.results || []) {
              await db.put("meal_time", objectUnproxy(item))
            }
          })
          .catch(async (err) => {
            const res = (await db.getAll("meal_time")) as MealTime[]
            this.meal_time = res
            reject(err)
          })
      })
    },
    async loadIngredientCategories(payload: object): Promise<PaginatedIngredientCategoryList> {
      const db = await getDB()
      if (!isOnline()) {
        const res = (await db.getAll("ing_categories")) as IngredientCategory[]
        this.ingredient_categories = res
        return new Promise((resolve) => {
          resolve(mockedPaginatedResponse(res, payload) as PaginatedIngredientCategoryList)
        })
      }
      return new Promise((resolve, reject) => {
        IngredientCategoryService.ingredientCategoryList(payload)
          .then(async (resp) => {
            this.ingredient_categories = resp.results as IngredientCategory[]
            resolve(resp)

            for (const item of resp.results || []) {
              await db.put("ing_categories", objectUnproxy(item))
            }
          })
          .catch(async (err: CustomAxiosError) => {
            this.ingredient_categories = (await db.getAll("ing_categories")) as IngredientCategory[]
            reject(err)
            handleErrors(err, "Ошибка загрузки списка категорий ингредиентоа")
          })
      })
    },
    async loadShops(payload: object): Promise<Shop[]> {
      const db = await getDB()
      if (!isOnline()) {
        this.shops = (await db.getAll("shops")) as Shop[]
        return new Promise((resolve) => {
          resolve(this.shops as Shop[])
        })
      }
      return new Promise((resolve, reject) => {
        ShopService.shopList(payload)
          .then(async (resp) => {
            this.shops = resp.results as Shop[]
            resolve(resp.results as Shop[])
            for (const item of resp.results || []) {
              await db.put("shops", objectUnproxy(item))
            }
          })
          .catch(async (err) => {
            reject(err)
            this.shops = (await db.getAll("shops")) as Shop[]
            return new Promise((resolve) => {
              resolve(this.shops as Shop[])
            })
          })
      })
    },

    // -- Recipes
    async loadRecipes(payload: object, loadMore = false): Promise<PaginatedRecipeReadList> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesList(payload)
          .then((resp) => {
            if (loadMore){
              if (!this.recipes){
                this.recipes = []
              }
              this.recipes = this.recipes.concat(resp.results as RecipeRead[])
            } else {
              this.recipes = resp.results as RecipeRead[]
            }
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadRecipe(id: number): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesRetrieve({ id })
          .then((resp) => {
            this.recipe = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async saveRecipe(payload: Recipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesPartialUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            this.recipe = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async patchRecipe(id: number, payload: PatchedRecipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesPartialUpdate({
          id,
          requestBody: payload,
        })
          .then((resp) => {
            this.recipe = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async createRecipe(payload: Recipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesCreate({ requestBody: payload })
          .then((resp) => {
            this.recipe = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async createRecipeImage(payload: FormData): Promise<RecipeImage> {
      return new Promise((resolve, reject) => {
        // RecipeImagesService.recipeImagesCreate({ requestBody: payload })
        request(OpenAPI, {
          method: "POST",
          url: "/api/v1/recipe_images/",
          formData: payload,
          mediaType: "application/json",
        })
          .then((resp) => {
            resolve(resp as RecipeImage)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadTags(payload: object): Promise<PaginatedRecipeTagList> {
      return new Promise((resolve, reject) => {
        RecipeTagsService.recipeTagsList(payload)
          .then((resp) => {
            this.tags = resp.results as RecipeTag[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    // Week plans
    async loadWeekPlan(payload: { year: number; week: number }): Promise<RecipePlanWeekRead> {
      const id = `${payload?.year}_${payload?.week}`
      if (!isOnline()) {
        const resObj = await recipePlansGetOffline(payload?.year, payload?.week)
        if (resObj) {
          this.week_plan = resObj
          return new Promise((resolve) => {
            resolve(resObj)
          })
        } else {
          Notify.create({
            type: "negative",
            caption: `Не найден сохраненный план для ${payload.year}.${payload.week}`,
          })
        }
      }
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekRetrieve({
          id: id,
        })
          .then((resp) => {
            this.week_plan = resp
            void recipePlansListUpdateFromServer(resp)
            resolve(resp)
          })
          .catch(async (err) => {
            const resObj = await recipePlansGetOffline(payload.year, payload.week)
            if (resObj) {
              this.week_plan = resObj
            }
            reject(err)
          })
      })
    },
    async loadWeekPlans(payload: object): Promise<PaginatedRecipePlanWeekReadList> {
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekList(payload)
          .then((resp) => {
            this.week_plans = resp.results as RecipePlanWeekRead[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async saveWeekPlan(payload: RecipePlanWeek): Promise<RecipePlanWeekRead> {
      const id = `${payload?.year}_${payload?.week}`
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekUpdate({
          id: id,
          requestBody: payload,
        })
          .then((resp) => {
            this.week_plan = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    // -- Products

    async loadProductListWeek(payload: { year: number; week: number }, no_save = false): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekRetrieve({ id: id })
          .then((resp) => {
            if (!no_save) {
              this.product_list = resp
            }
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadProductListWeeks(payload: object): Promise<PaginatedProductListWeekReadList> {
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekList(payload)
          .then((resp) => {
            this.product_lists = resp.results as ProductListWeekRead[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async saveProductListWeek(payload: { year: number; week: number } & ProductListWeek): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekUpdate({
          id: id,
          requestBody: payload,
        })
          .then((resp) => {
            this.product_list = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async generateProductListWeek(payload: { year: number; week: number }): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekGenerateRetrieve({ id: id })
          .then((resp) => {
            this.product_list = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async productListSend(payload: { year: number; week: number }): Promise<void> {
      return new Promise<void>((resolve, reject) => {
        const id = `${payload?.year}_${payload?.week}`
        ProductListWeekService.productListWeekSendListRetrieve({ id })
          .then(() => {
            resolve()
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async loadProductListItems(payload: object): Promise<PaginatedProductListItemReadList> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemList(payload)
          .then((resp) => {
            this.product_list_items = resp.results as ProductListItemRead[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async loadProductListItem(id: number): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemRetrieve({ id })
          .then((resp) => {
            this.product_list_item = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async createProductListItem(payload: ProductListItem): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemCreate({ requestBody: payload })
          .then((resp) => {
            this.product_list_item = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async updateProductListItem(payload: ProductListItem): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            this.product_list_item = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    // eslint-disable-next-line @typescript-eslint/require-await
    async syncProductListItems(items: ProductListItemSyncable[], callback?: CallableFunction, callbackRes?: CallableFunction): Promise<void> {
      return new Promise((resolve, reject) => {
        items.forEach((item, index) => {
          if (!item.changed) {
            return
          }
          const itemExists = item.id
          const itemCleared = itemExists ? (onlyChangedFields(item, item.changed) as ProductListItemRead) : item
          if (callback) {
            callback(index)
          }
          let prom
          console.debug("Performing sync for item: ", index, itemCleared, item)

          if (itemExists) {
            prom = ProductListItemService.productListItemPartialUpdate({
              id: item.id,
              requestBody: productListItemFromRead(itemCleared),
            })
          } else {
            prom = ProductListItemService.productListItemCreate({ requestBody: productListItemFromRead(itemCleared) })
          }

          prom
            .then((resp) => {
              if (callbackRes) {
                callbackRes(item, resp)
              }
              // this.product_list_item = resp
            })
            .catch((err: CustomAxiosError) => {
              handleErrors(err)
              reject(err)
            })
        })
        resolve()
      })
    },
    async deleteProductListItem(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemDestroy({ id })
          .then(() => {
            resolve()
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    // Ingredients

    async loadIngredients(payload: object, search = false): Promise<PaginatedIngredientReadList> {
      const db = await getDB()

      this.ingredients_searched = search
      if (!isOnline()) {
        const res = (await db.getAll("ingredients")) as IngredientRead[]
        this.ingredients = res
        return new Promise((resolve) => {
          resolve(mockedPaginatedResponse(res) as PaginatedIngredientReadList)
        })
      }
      return new Promise((resolve, reject) => {
        const defaultPayload = {
          pageSize: 1000,
        }
        IngredientsService.ingredientsList(Object.assign({}, defaultPayload, payload))
          .then(async (resp) => {
            this.ingredients = resp.results as IngredientRead[]
            resolve(resp)

            if (!search) {
              for (const item of resp.results || []) {
                await db.put("ingredients", objectUnproxy(item))
              }
            }
          })
          .catch(async (err) => {
            this.ingredients = (await db.getAll("ingredients")) as IngredientRead[]
            reject(err)
          })
      })
    },
    async loadIngredient(id: number): Promise<IngredientRead> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsRetrieve({ id })
          .then((resp) => {
            this.ingredient = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async saveIngredient(payload: Ingredient): Promise<IngredientRead> {
      return new Promise((resolve, reject) => {
        request(OpenAPI, {
          method: "PUT",
          url: "/api/v1/ingredients/{id}/",
          path: {
            id: payload.id,
          },
          formData: payload,
          mediaType: "application/json",
        })
          // IngredientsService.ingredientsUpdate({
          //   id: payload.id,
          //   requestBody: payload,
          // })
          .then((resp) => {
            this.ingredient = resp as IngredientRead
            resolve(resp as IngredientRead)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async createIngredient(payload: Ingredient): Promise<IngredientRead> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsCreate({ requestBody: payload })
          .then((resp) => {
            this.ingredient = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async deleteIngredient(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsDestroy({ id })
          .then(() => {
            resolve()
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    // Tasks

    async loadTaskCategories(payload: object): Promise<PaginatedTaskCategoryList> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryList(payload)
          .then((resp) => {
            this.tasks_categories = resp.results as TaskCategory[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async createTaskCategory(payload: TaskCategory): Promise<TaskCategory> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryCreate({ requestBody: payload })
          .then((resp) => {
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async updateTaskCategory(payload: TaskCategory): Promise<TaskCategory> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async deleteTaskCategory(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryDestroy({ id: id })
          .then(() => {
            resolve()
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadTasks(payload: object): Promise<PaginatedTaskNestedList> {
      return new Promise((resolve, reject) => {
        TaskService.taskList(payload)
          .then((resp) => {
            this.tasks = resp.results as Task[]
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async loadTask(id: number): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskRetrieve({ id })
          .then((resp) => {
            this.task = resp as Task
            resolve(resp as Task)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async createTask(payload: Task): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskCreate({ requestBody: payload })
          .then((resp) => {
            this.task = resp as Task
            resolve(resp as Task)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async updateTask(payload: Task): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskUpdate({ id: payload.id, requestBody: payload })
          .then((resp) => {
            this.task = resp as Task
            resolve(resp as Task)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
    async deleteTask(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        TaskService.taskDestroy({ id })
          .then(() => {
            resolve()
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async loadConditions(payload: object): Promise<WeekPlanCondition[]> {
      if (!isOnline()) {
        const res: WeekPlanCondition[] | null = LocalStorage.getItem("cached:conditions")
        if (res) {
          this.conditions = res
          return new Promise((resolve) => {
            resolve(this.conditions as WeekPlanCondition[])
          })
        }
      }
      return new Promise((resolve, reject) => {
        ConditionsService.conditionsList(payload)
          .then((resp) => {
            this.conditions = resp.results as WeekPlanCondition[]
            resolve(resp.results as WeekPlanCondition[])
            LocalStorage.set("cached:conditions", resp.results)
          })
          .catch((err) => {
            reject(err)
            const res: WeekPlanCondition[] | null = LocalStorage.getItem("cached:conditions")
            if (res) {
              this.conditions = res
              return new Promise((resolve) => {
                resolve(this.conditions as WeekPlanCondition[])
              })
            }
          })
      })
    },
  },
})
