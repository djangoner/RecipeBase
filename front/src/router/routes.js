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
            year: "int:",
            week: "int:",
          },
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
