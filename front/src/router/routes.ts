const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      {
        path: "",
        component: () => import("pages/IndexPage.vue"),
        name: "index",
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: "/recipes",
        component: () => import("src/pages/RecipesList.vue"),
        name: "recipes",
        meta: {
          requiresAuth: true,
          query: {
            compilation: "string:",
            display: "string:cards",
          },
        },
      },
      {
        path: "/recipes/:id",
        component: () => import("pages/RecipeView.vue"),
        name: "recipe",
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: "/week_plan",
        component: () => import("pages/WeekPlan.vue"),
        name: "week_plan",
        meta: {
          requiresAuth: true,
          query: {
            year: "int:",
            week: "int:",
          },
        },
      },
      {
        path: "/product_list",
        component: () => import("pages/ProductList.vue"),
        name: "product_list",
        meta: {
          requiresAuth: true,
          query: {
            task: "int:",
            shop: "int:",
            year: "int:",
            week: "int:",
          },
        },
      },
      {
        path: "/tasks",
        component: () => import("pages/TasksList.vue"),
        name: "tasks",
        meta: {
          requiresAuth: true,
          query: {
            task: "int:",
          },
        },
      },
      {
        path: "/ingredients",
        component: () => import("pages/IngredientsList.vue"),
        name: "ingredients",
        meta: {
          requiresAuth: true,
          query: {
            q: "string:",
            hasPrice: "string:",
            hasRecipes: "string:",
            hasCategory: "string:",
            category: "string:",
            needBuy: "string:",
            edible: "string:",
          },
        },
      },
      {
        path: "/ingredients/:id",
        component: () => import("pages/IngredientView.vue"),
        name: "ingredient",
        meta: {
          requiresAuth: true,
        },
      },
    ],
  },

  {
    path: "/",
    component: () => import("layouts/EmptyLayout.vue"),
    children: [
      {
        path: "/login",
        component: () => import("pages/AccountLogin.vue"),
        name: "login",
      },
    ],
  },

  // 404
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
