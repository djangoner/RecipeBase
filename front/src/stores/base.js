import { defineStore } from "pinia";
import { api } from "src/boot/axios";

export const useBaseStore = defineStore("base", {
  state: () => ({
    recipes: null,
    recipe: null,
    tags: null,
    ingredients: null,
    amount_types: null,
    week_plan: null,
    week_plans: null,
    meal_time: null,
    product_list: null,
    product_lists: null,
    product_list_items: null,
    product_list_item: null,
    tasks: null,
    task: null,
    tasks_categories: null,
  }),

  getters: {},

  actions: {
    // -- Essentials
    async loadIngredients(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/ingredients/", { params: payload })
          .then((resp) => {
            this.ingredients = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadAmountTypes(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/ingredients/amount_types/", { params: payload })
          .then((resp) => {
            this.amount_types = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadMealTime(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("meal_time", {
            params: payload,
          })
          .then((resp) => {
            this.meal_time = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // -- Recipes
    async loadRecipes(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/recipes/", { params: payload })
          .then((resp) => {
            this.recipes = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadRecipe(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/recipes/" + payload.id + "/", { params: payload })
          .then((resp) => {
            this.recipe = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveRecipe(payload, id) {
      return new Promise((resolve, reject) => {
        api
          .patch("/recipes/" + (payload.id || id) + "/", payload)
          .then((resp) => {
            this.recipe = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createRecipe(payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/recipes/", payload)
          .then((resp) => {
            this.recipe = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createRecipeImage(payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/recipe_images/", payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTags(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/recipe_tags/", { params: payload })
          .then((resp) => {
            this.tags = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // Week plans
    async loadWeekPlan(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/recipe_plan_week/${payload.year}_${payload.week}/`, {
            params: payload,
          })
          .then((resp) => {
            this.week_plan = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadWeekPlans(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/recipe_plan_week/`, {
            params: payload,
          })
          .then((resp) => {
            this.week_plans = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveWeekPlan(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch(`/recipe_plan_week/${payload.year}_${payload.week}/`, payload)
          .then((resp) => {
            this.week_plan = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    // -- Products

    async loadProductListWeek(payload, no_save) {
      return new Promise((resolve, reject) => {
        api
          .get(`/product_list_week/${payload.year}_${payload.week}/`, {
            params: payload,
          })
          .then((resp) => {
            if (!no_save) {
              this.product_list = resp.data;
            }
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadProductListWeeks(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/product_list_week/`, {
            params: payload,
          })
          .then((resp) => {
            this.product_lists = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async saveProductListWeek(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch(`/product_list_week/${payload.year}_${payload.week}/`, payload)
          .then((resp) => {
            this.product_list = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async generateProductListWeek(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/product_list_week/${payload.year}_${payload.week}/generate/`, {
            params: payload,
          })
          .then((resp) => {
            this.product_list = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadProductListItems(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/product_list_item/", {
            params: payload,
          })
          .then((resp) => {
            this.product_list_items = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadProductListItem(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/product_list_item/${payload.id}/`, {
            params: payload,
          })
          .then((resp) => {
            this.product_list_item = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async createProductListItem(payload) {
      return new Promise((resolve, reject) => {
        api
          .post(`/product_list_item/`, payload)
          .then((resp) => {
            this.product_list_item = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateProductListItem(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch(`/product_list_item/${payload.id}/`, payload)
          .then((resp) => {
            this.product_list_item = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteProductListItem(payload) {
      return new Promise((resolve, reject) => {
        api
          .delete(`/product_list_item/${payload.id}/`, payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    // Tasks

    async loadTaskCategories(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/task_category/", { params: payload })
          .then((resp) => {
            this.tasks_categories = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createTaskCategory(payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/task_category/", payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateTaskCategory(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch("/task_category/" + payload.id + "/", payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteTaskCategory(payload) {
      return new Promise((resolve, reject) => {
        api
          .delete("/task_category/" + payload.id + "/", payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTasks(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/task/", { params: payload })
          .then((resp) => {
            this.tasks = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async loadTask(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/task/" + payload.id + "/", { params: payload })
          .then((resp) => {
            this.task = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async createTask(payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/task/", payload)
          .then((resp) => {
            this.task = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateTask(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch("/task/" + payload.id + "/", payload)
          .then((resp) => {
            this.task = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async deleteTask(payload) {
      return new Promise((resolve, reject) => {
        api
          .delete("/task/" + payload.id + "/", payload)
          .then((resp) => {
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
});
