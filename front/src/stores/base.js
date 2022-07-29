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
    meal_time: null,
    product_list: null,
    product_list_items: null,
    product_list_item: null,
  }),

  getters: {},

  actions: {
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
    async loadProductListWeek(payload) {
      return new Promise((resolve, reject) => {
        api
          .get(`/product_list_week/${payload.year}_${payload.week}/`, {
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
  },
});
