import { AxiosError, AxiosResponse } from "axios";
import { route } from "quasar/wrappers";
import { useAuthStore } from "src/stores/auth";
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import routes from "./routes";
/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });
  const store = useAuthStore()

  Router.beforeEach((to, from, next) => {
    store.pageLoading = true
    const isAuthorized = store.isAuthenticated
    const routerLogout = () => {
      void store.logout().then(() => {
        void Router.push({
          name: "login",
          query: { next: to.fullPath },
        })
      })
    }

    if (isAuthorized && !store.account) {
      console.debug("Checking user account...")
      store.loadAccountInfo().catch((err: AxiosError | AxiosResponse) => {
        if ("response" in err) {
          if (!err.response && (!err.code || err.code === "ERR_NETWORK" || err.code == "ERR_INTERNET_DISCONNECTED")) {
            // Ignore internet errors
          } else {
            console.debug("Unknown error, logging out...")
            routerLogout()
          }
        } else if ("status" in err) {
          if (err.status == 401) {
            console.debug("Unauthorized, logging out...")
            routerLogout()
          }
        } else {
          console.debug("Unknown error type, logging out...")
          routerLogout()
        }
      })
    }

    if (to.matched.some((record) => record.meta.requiresAuth) && !isAuthorized) {
      next({ name: "login", query: { next: to.fullPath } })
    } else if (to.name === "login" && isAuthorized) {
      next({ name: "index" })
    } else {
      next()
    }
  })

  Router.afterEach(() => {
    store.pageLoading = false
  })

  return Router;
});
