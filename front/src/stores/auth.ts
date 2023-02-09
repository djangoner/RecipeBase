import { defineStore } from "pinia";
import {
  AuthService,
  AuthToken,
  PaginatedUserList,
  User,
  UsersService,
} from "src/client";
import { OpenAPI } from "src/client";

// eslint-disable-next-line @typescript-eslint/require-await
const getToken = async () => {
  return localStorage.getItem("authToken") || "";
};

OpenAPI.TOKEN = getToken;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    authToken: localStorage.getItem("authToken"),
    account: null as User | null,
    users: null as Array<User> | null,
  }),

  getters: {
    isAuthenticated(state) {
      return !!state.authToken;
    },
    permissions(state): Array<string> {
      return state.account?.permissions || [];
    },
  },

  actions: {
    hasPerm(perm: string): boolean {
      return this.permissions.includes(perm);
    },

    async logout(): Promise<void> {
      return new Promise((resolve) => {
        this.authToken = null;
        localStorage.removeItem("authToken");
        resolve();
      });
    },

    async login(payload: AuthToken): Promise<AuthToken> {
      return new Promise((resolve, reject) => {
        AuthService.authTokenCreate({ formData: payload })
          .then((resp) => {
            const token: string = resp.token;

            localStorage.setItem("authToken", token);
            this.authToken = token;

            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadAccountInfo(): Promise<User> {
      return new Promise((resolve, reject) => {
        UsersService.usersCurrentUserInfoRetrieve()
          .then((resp) => {
            this.account = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },

    async loadUsers(payload: object): Promise<PaginatedUserList> {
      return new Promise((resolve, reject) => {
        UsersService.usersList(payload)
          .then((resp) => {
            this.users = resp.results as Array<User>;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    async updateAccountInfo(user: User): Promise<User> {
      return new Promise((resolve, reject) => {
        UsersService.usersUpdate({ id: user?.id, requestBody: user })
          .then((resp) => {
            this.account = resp;
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
});
