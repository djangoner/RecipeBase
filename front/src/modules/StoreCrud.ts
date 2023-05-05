// Pinia store crud v0.11
import { Ref } from "vue"
import { CustomAxiosError, handleErrors } from "./HandleErrorsMixin"

interface StoreShortcutParams {
  action?: string
  variable?: unknown
  listVariable?: unknown
  idField?: string
  setValue?: CallableFunction
  promise: Promise<unknown>
  errorTitle?: string
  isResults?: boolean
  isDestroy?: boolean
}

export const actionsAll = ["list", "retrieve", "create", "update", "delete"]

function setVariable<T>(variable: unknown, value: unknown) {
  variable = value
  return value as T
}

function getValue<T>(params: StoreShortcutParams, resp: unknown) {
  if (params.isDestroy) {
    return null
  } else if (params.isResults) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    // @ts-expect-error ignore
    return resp.results as T
  }

  return resp
}

export function storeShortcut<T>(params: StoreShortcutParams): Promise<T> {
  /* Shortcut for handling REST endpoint and saving result to store */

  return new Promise((resolve, reject) => {
    params.promise
      .then((resp) => {
        const value = getValue<T>(params, resp)
        // console.debug('Set variable: ', params, value);
        if (params.variable !== undefined) {
          setVariable<T>(params.variable, value)
          // params.variable = isDestroy? null : (params.isResults ? resp.results : resp);
        } else if (params.setValue !== undefined) {
          params.setValue(value)
        }
        resolve(resp as T)
      })
      .catch((err: CustomAxiosError) => {
        handleErrors(err, params.errorTitle)
        reject(err)
      })
  })
}

export function storeItemsTryUpdate(items: Array<unknown> | null, item: unknown, idField = "id"): boolean {
  /* Try to update item in list of items. Using example: list endpoint */
  if (items) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const foundIndex = items.findIndex((c) => c[idField] === item[idField])
    if (foundIndex !== undefined) {
      items[foundIndex] = item
      return true
    }
  }
  return false
}

export function storeItemsTryDelete(items: Array<unknown> | null, idValue: unknown, idField = "id"): boolean {
  /* Try to delete item from list of items. Using example: delete endpoint. */
  if (items) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const foundIndex = items.findIndex((c) => c[idField] === idValue)
    if (foundIndex !== undefined) {
      items.splice(foundIndex, 1)
      return true
    }
  }
  return false
}

export function storeItemsConcat<T>(items: Array<T> | null, results: Array<T>): Array<T> {
  /* Concat new results with old store results. Using example: logs, chat. */
  let res: T[] = []
  if (items) {
    res = items.concat(results)
  } else {
    res = results
  }
  return res
}

export function promiseSetLoading(prom: Promise<unknown>, loadingVar: Ref<boolean>) {
  loadingVar.value = true
  prom.finally(() => {
    loadingVar.value = false
  })
}
