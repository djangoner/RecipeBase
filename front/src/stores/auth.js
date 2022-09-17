import { defineStore } from "pinia";
import { api } from "src/boot/axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    authToken: localStorage.getItem("authToken"),
    account: null,
    users: null,
  }),

  getters: {
    isAuthenticated(state) {
      return !!state.authToken;
    },
  },

  actions: {
    async logout() {
      return new Promise((resolve, reject) => {
        this.authToken = null;
        localStorage.removeItem("authToken");
        delete api.defaults.headers.common["Authorization"];
        resolve();
      });
    },

    async login(payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/auth/token/", payload)
          .then((resp) => {
            const token = resp.data.token;

            localStorage.setItem("authToken", token);
            api.defaults.headers.common["Authorization"] = "Token  " + token;
            this.authToken = token;

            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadAccountInfo() {
      return new Promise((resolve, reject) => {
        api
          .get("/users/current_user_info/")
          .then((resp) => {
            this.account = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadUsers(payload) {
      return new Promise((resolve, reject) => {
        api
          .get("/users/", { params: payload })
          .then((resp) => {
            this.users = resp.data;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateAccountInfo(payload) {
      return new Promise((resolve, reject) => {
        api
          .patch("/auth/account", payload)
          .then((resp) => {
            Object.assign(this.account, resp.data);
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
});
