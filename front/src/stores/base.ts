import { defineStore } from "pinia";
import {
  AmountTypes,
  Ingredient,
  IngredientCategory,
  IngredientCategoryService,
  IngredientsService,
  MealTime,
  MealTimeService,
  PaginatedIngredientCategoryList,
  PaginatedRecipeList,
  PaginatedRecipeTagList,
  PaginatedShopList,
  ProductListItem,
  ProductListItemService,
  ProductListWeek,
  ProductListWeekService,
  Recipe,
  RecipeImage,
  RecipeImagesService,
  RecipePlanWeek,
  RecipePlanWeekService,
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
} from "src/client";

export const useBaseStore = defineStore("base", {
  state: () => ({
    stats: null as StatsList | null,
    recipes: null as Recipe[] | null,
    recipe: null as Recipe | null,
    tags: null as RecipeTag[] | null,
    amount_types: null as AmountTypes | null,
    week_plan: null as RecipePlanWeek | null,
    week_plans: null as RecipePlanWeek[] | null,
    meal_time: null as MealTime | null,
    product_list: null as ProductListWeek | null,
    product_lists: null as ProductListWeek[] | null,
    product_list_items: null as ProductListItem[] | null,
    product_list_item: null as ProductListItem | null,
    ingredients: null as Ingredient[] | null,
    ingredient: null as Ingredient | null,
    tasks: null as Task[] | null,
    task: null as Task | null,
    tasks_categories: null as TaskCategory[] | null,
    ingredient_categories: null as IngredientCategory[] | null,
    shops: null as Shop[] | null,
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
    async loadMealTime(id: number): Promise<MealTime> {
      return new Promise((resolve, reject) => {
        MealTimeService.mealTimeRetrieve({ id })
          .then((resp) => {
            this.meal_time = resp;
            resolve(resp);
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
    async loadRecipes(payload: object): Promise<PaginatedRecipeList> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesList(payload)
          .then((resp) => {
            this.recipes = resp.results as Recipe[];
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadRecipe(id: number): Promise<Recipe> {
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
    async saveRecipe(id: number, payload: Recipe): Promise<Recipe> {
      return new Promise((resolve, reject) => {
        RecipesService.recipesUpdate({ id, requestBody: payload })
          .then((resp) => {
            this.recipe = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createRecipe(payload: Recipe): Promise<Recipe> {
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
    async createRecipeImage(payload: RecipeImage): Promise<RecipeImage> {
      return new Promise((resolve, reject) => {
        RecipeImagesService.recipeImagesCreate({ requestBody: payload })
          .then((resp) => {
            resolve(resp);
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
    }): Promise<RecipePlanWeek> {
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
    async loadWeekPlans(payload: object): Promise<RecipePlanWeek[]> {
      return new Promise((resolve, reject) => {
        RecipePlanWeekService.recipePlanWeekList(payload)
          .then((resp) => {
            this.week_plans = resp.results as RecipePlanWeek[];
            resolve(resp as RecipePlanWeek[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveWeekPlan(payload: RecipePlanWeek): Promise<RecipePlanWeek> {
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
    ): Promise<ProductListWeek> {
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
    async loadProductListWeeks(payload: object): Promise<ProductListWeek[]> {
      return new Promise((resolve, reject) => {
        ProductListWeekService.productListWeekList(payload)
          .then((resp) => {
            this.product_lists = resp.results as ProductListWeek[];
            resolve(resp.results as ProductListWeek[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveProductListWeek(
      payload: { year: number; week: number } & ProductListWeek
    ): Promise<ProductListWeek> {
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
    }): Promise<ProductListWeek> {
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

    async loadProductListItems(payload: object): Promise<ProductListItem[]> {
      return new Promise((resolve, reject) => {
        ProductListItemService.productListItemList(payload)
          .then((resp) => {
            this.product_list_items = resp.results as ProductListItem[];
            resolve(resp as ProductListItem[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadProductListItem(id: number): Promise<ProductListItem> {
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
    ): Promise<ProductListItem> {
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
    ): Promise<ProductListItem> {
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

    async loadIngredients(payload: object): Promise<Ingredient[]> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsList(payload)
          .then((resp) => {
            this.ingredients = resp.results as Ingredient[];
            resolve(resp.results as Ingredient[]);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadIngredient(id: number): Promise<Ingredient> {
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
    async saveIngredient(id: number, payload: Ingredient): Promise<Ingredient> {
      return new Promise((resolve, reject) => {
        IngredientsService.ingredientsUpdate({ id, requestBody: payload })
          .then((resp) => {
            this.ingredient = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createIngredient(payload: Ingredient): Promise<Ingredient> {
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

    async loadTaskCategories(payload: object): Promise<TaskCategory[]> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryList(payload)
          .then((resp) => {
            this.tasks_categories = resp.results as TaskCategory[];
            resolve(resp.results as TaskCategory[]);
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
    async updateTaskCategory(
      id: number,
      payload: TaskCategory
    ): Promise<TaskCategory> {
      return new Promise((resolve, reject) => {
        TaskCategoryService.taskCategoryUpdate({ id, requestBody: payload })
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
    async loadTasks(payload: object): Promise<Task[]> {
      return new Promise((resolve, reject) => {
        TaskService.taskList(payload)
          .then((resp) => {
            this.tasks = resp.results as Task[];
            resolve(resp.results as Task[]);
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
    async updateTask(id: number, payload: Task): Promise<Task> {
      return new Promise((resolve, reject) => {
        TaskService.taskUpdate({ id, requestBody: payload })
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
  },
});
