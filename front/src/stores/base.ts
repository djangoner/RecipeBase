import { defineStore } from "pinia";
import {
  AmountTypes,
  CancelablePromise,
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
  PaginatedShopList,
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
} from "src/client";
import { request } from "src/client/core/request";

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

  getters: {},

  actions: {
    // -- Essentials

    async loadStats(): Promise<StatsList> {
      return new Promise((resolve, reject) => {
        StatsService.statsList()
          .then((resp) => {
            const stat = resp[0] || resp;
            this.stats = stat;
            resolve(stat);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadAmountTypes(): Promise<AmountTypes> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsAmountTypesRetrieve()
          .then((resp) => {
            this.amount_types = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadMealTime(payload: object): Promise<MealTime[]> {
      return new Promise((resolve, reject) => {
        MealTimeService.mealTimeList(payload)
          .then((resp) => {
            this.meal_time = resp.results as MealTime[];
            resolve(resp as MealTime[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadIngredientCategories(
      payload: object
    ): Promise<PaginatedIngredientCategoryList> {
      return new Promise((resolve, reject) => {
        IngredientCategoryService.ingredientCategoryList(payload)
          .then((resp) => {
            this.ingredient_categories = resp.results as IngredientCategory[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadShops(payload: object): Promise<PaginatedShopList> {
      return new Promise((resolve, reject) => {
        ShopService.shopList(payload)
          .then((resp) => {
            this.shops = resp.results as Shop[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // -- Recipes
    async loadRecipes(payload: object): Promise<PaginatedRecipeReadList> {
      // return new CancelablePromise<PaginatedRecipeReadList>(
      //   (resolve, reject) => {
      //     request(OpenAPI, {
      //       method: "GET",
      //       url: "/api/v1/recipes/",
      //       query: payload,
      //     })
      //       .then((resp) => {
      //         this.recipes = (resp as PaginatedRecipeReadList)
      //           .results as RecipeRead[];
      //         resolve(resp as PaginatedRecipeReadList);
      //       })
      //       .catch((err) => {
      //         reject(err);
      //       });
      //   }
      // );
      return new Promise((resolve, reject) => {
        RecipesService.recipesList(payload)
          .then((resp) => {
            this.recipes = resp.results as RecipeRead[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadRecipe(id: number): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesRetrieve({ id })
          .then((resp) => {
            this.recipe = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveRecipe(payload: Recipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesPartialUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            this.recipe = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async patchRecipe(id: number, payload: PatchedRecipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesPartialUpdate({
          id,
          requestBody: payload,
        })
          .then((resp) => {
            this.recipe = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createRecipe(payload: Recipe): Promise<RecipeRead> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesCreate({ requestBody: payload })
          .then((resp) => {
            this.recipe = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
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
            resolve(resp as RecipeImage);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTags(payload: object): Promise<PaginatedRecipeTagList> {
      return new Promise((resolve, reject) => {
        RecipeTagsService.recipeTagsList(payload)
          .then((resp) => {
            this.tags = resp.results as RecipeTag[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // Week plans
    async loadWeekPlan(payload: {
      year: number;
      week: number;
    }): Promise<RecipePlanWeekRead> {
      const id = `${payload?.year}_${payload?.week}`;
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekRetrieve({
          id: id,
        })
          .then((resp) => {
            this.week_plan = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadWeekPlans(
      payload: object
    ): Promise<PaginatedRecipePlanWeekReadList> {
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekList(payload)
          .then((resp) => {
            this.week_plans = resp.results as RecipePlanWeekRead[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveWeekPlan(payload: RecipePlanWeek): Promise<RecipePlanWeekRead> {
      const id = `${payload?.year}_${payload?.week}`;
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekUpdate({
          id: id,
          requestBody: payload,
        })
          .then((resp) => {
            this.week_plan = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // -- Products

    async loadProductListWeek(
      payload: { year: number; week: number },
      no_save = false
    ): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`;
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekRetrieve({ id: id })
          .then((resp) => {
            if (!no_save) {
              this.product_list = resp;
            }
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadProductListWeeks(
      payload: object
    ): Promise<PaginatedProductListWeekReadList> {
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekList(payload)
          .then((resp) => {
            this.product_lists = resp.results as ProductListWeekRead[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveProductListWeek(
      payload: { year: number; week: number } & ProductListWeek
    ): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`;
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekUpdate({
          id: id,
          requestBody: payload,
        })
          .then((resp) => {
            this.product_list = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async generateProductListWeek(payload: {
      year: number;
      week: number;
    }): Promise<ProductListWeekRead> {
      const id = `${payload?.year}_${payload?.week}`;
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekGenerateRetrieve({ id: id })
          .then((resp) => {
            this.product_list = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async productListSend(payload: {
      year: number;
      week: number;
    }): Promise<void> {
      return new Promise<void>((resolve, reject) => {
        const id = `${payload?.year}_${payload?.week}`;
        ProductListWeekService.productListWeekSendListRetrieve({ id })
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadProductListItems(
      payload: object
    ): Promise<PaginatedProductListItemReadList> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemList(payload)
          .then((resp) => {
            this.product_list_items = resp.results as ProductListItemRead[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadProductListItem(id: number): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemRetrieve({ id })
          .then((resp) => {
            this.product_list_item = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async createProductListItem(
      payload: ProductListItem
    ): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemCreate({ requestBody: payload })
          .then((resp) => {
            this.product_list_item = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateProductListItem(
      payload: ProductListItem
    ): Promise<ProductListItemRead> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            this.product_list_item = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteProductListItem(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemDestroy({ id })
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // Ingredients

    async loadIngredients(
      payload: object,
      search = false
    ): Promise<PaginatedIngredientReadList> {
      this.ingredients_searched = search;
      return new Promise((resolve, reject) => {
        const defaultPayload = {
          pageSize: 1000,
        };
        IngredientsService.ingredientsList(
          Object.assign({}, defaultPayload, payload)
        )
          .then((resp) => {
            this.ingredients = resp.results as IngredientRead[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadIngredient(id: number): Promise<IngredientRead> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsRetrieve({ id })
          .then((resp) => {
            this.ingredient = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
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
            this.ingredient = resp as IngredientRead;
            resolve(resp as IngredientRead);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createIngredient(payload: Ingredient): Promise<IngredientRead> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsCreate({ requestBody: payload })
          .then((resp) => {
            this.ingredient = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteIngredient(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsDestroy({ id })
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // Tasks

    async loadTaskCategories(
      payload: object
    ): Promise<PaginatedTaskCategoryList> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryList(payload)
          .then((resp) => {
            this.tasks_categories = resp.results as TaskCategory[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createTaskCategory(payload: TaskCategory): Promise<TaskCategory> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryCreate({ requestBody: payload })
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateTaskCategory(payload: TaskCategory): Promise<TaskCategory> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryUpdate({
          id: payload.id,
          requestBody: payload,
        })
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteTaskCategory(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryDestroy({ id: id })
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTasks(payload: object): Promise<PaginatedTaskNestedList> {
      return new Promise((resolve, reject) => {
        TaskService.taskList(payload)
          .then((resp) => {
            this.tasks = resp.results as Task[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTask(id: number): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskRetrieve({ id })
          .then((resp) => {
            this.task = resp as Task;
            resolve(resp as Task);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createTask(payload: Task): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskCreate({ requestBody: payload })
          .then((resp) => {
            this.task = resp as Task;
            resolve(resp as Task);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateTask(payload: Task): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskUpdate({ id: payload.id, requestBody: payload })
          .then((resp) => {
            this.task = resp as Task;
            resolve(resp as Task);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteTask(id: number): Promise<void> {
      return new Promise((resolve, reject) => {
        TaskService.taskDestroy({ id })
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadConditions(payload: object): Promise<WeekPlanCondition[]> {
      return new Promise((resolve, reject) => {
        ConditionsService.conditionsList(payload)
          .then((resp) => {
            this.conditions = resp.results as WeekPlanCondition[];
            resolve(resp.results as WeekPlanCondition[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
});
