import { defineStore } from "pinia"
import { AuthService, AuthToken, User, UsersService } from "src/client"
import { LocalStorage } from "quasar"
import { OpenAPI } from "src/client"
import { CustomAxiosError, handleErrors } from "src/modules/HandleErrorsMixin"

// eslint-disable-next-line @typescript-eslint/require-await
const getToken = async () => {
  return localStorage.getItem("authToken") || ""
}

OpenAPI.TOKEN = getToken

const cachedPermissions: string[] = LocalStorage.getItem("cachedPermissions") || []
const isOnline = () => navigator?.onLine

export const useAuthStore = defineStore("auth", {
  state: () => ({
    authToken: localStorage.getItem("authToken"),
    account: null as User | null,
    users: null as Array<User> | null,
  }),

  getters: {
    isAuthenticated(state) {
      return !!state.authToken
    },
    permissions(state): Array<string> {
      return state.account?.permissions || []
    },
  },

  actions: {
    hasPerm(perm: string): boolean {
      if (this.account?.is_superuser) {
        return true
      }
      const perms = this.permissions.length > 0 ? this.permissions : cachedPermissions
      return perms.includes(perm)
    },

    async logout(): Promise<void> {
      return new Promise((resolve) => {
        this.authToken = null
        localStorage.removeItem("authToken")
        resolve()
      })
    },

    async login(payload: AuthToken): Promise<AuthToken> {
      return new Promise((resolve, reject) => {
        AuthService.authTokenCreate({ formData: payload })
          .then((resp) => {
            const token: string = resp.token

            localStorage.setItem("authToken", token)
            this.authToken = token

            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async loadAccountInfo(): Promise<User> {
      return new Promise((resolve, reject) => {
        UsersService.usersCurrentUserInfoRetrieve()
          .then((resp) => {
            this.account = resp
            LocalStorage.set("cachedPermissions", resp.permissions)
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },

    async loadUsers(payload: object): Promise<User[]> {
      if (!isOnline()) {
        const res: User[] | null = LocalStorage.getItem("cached:users")
        if (res) {
          this.users = res
          return new Promise((resolve) => {
            resolve(this.users as User[])
          })
        }
      }
      return new Promise((resolve, reject) => {
        UsersService.usersList(payload)
          .then((resp) => {
            this.users = resp.results as Array<User>
            resolve(resp.results as User[])
            LocalStorage.set("cached:users", resp.results)
          })
          .catch((err: CustomAxiosError) => {
            handleErrors(err, "Ошибка загрузки пользователей")
            reject(err)
            const res: User[] | null = LocalStorage.getItem("cached:users")
            if (res) {
              this.users = res
              return new Promise((resolve) => {
                resolve(this.users as User[])
              })
            }
          })
      })
    },
    async updateAccountInfo(user: User): Promise<User> {
      return new Promise((resolve, reject) => {
        UsersService.usersUpdate({ id: user?.id, requestBody: user })
          .then((resp) => {
            this.account = resp
            resolve(resp)
          })
          .catch((err) => {
            reject(err)
          })
      })
    },
  },
})
