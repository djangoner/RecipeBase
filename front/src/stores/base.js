import { defineStore } from "pinia";
import { api } from "src/boot/axios";

export const useBaseStore = defineStore("base", {
  state: () => ({
    recipes: null,
    recipe: null,
    tags: null,
    ingredients: null,
    amount_types: null,
  }),

  getters: {},

  actions: {
    async loadRecipes(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/recipes", { params: payload })
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
          .get("/recipes/" + payload.id, { params: payload })
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
  },
});
