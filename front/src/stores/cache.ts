import { defineStore } from "pinia"
import { SessionStorage } from "quasar"
import { RecipeRead } from "src/client"
import { stringify, parse } from "zipson"

type CacheKey = string | object
type CacheValue = object

interface CacheMeta {
  value: CacheValue
  valid_until: number // Timestamp
  // ttl: number
}
type CacheData = Map<string, CacheMeta>

const DEFAULT_TIMEOUT = 60 * 5 * 1000
const UPDATE_CLEARED_TIMEOUT = 30 * 1000

function readCache(): CacheData {
  const rawString: string = SessionStorage.getItem("CacheStorage") || ""
  const data = new Map(Object.entries((parse(rawString) as object) || {})) as CacheData
  console.debug("Read cache: ", rawString.length)
  return data
}

export const useCacheStore = defineStore("cache", {
  state() {
    return {
      cacheData: readCache(),
      lastCleared: 0,
    }
  },
  getters: {
    getCached: (state) => (key: CacheKey) => {
      const meta = state.cacheData.get(JSON.stringify(key))
      if (!meta) {
        return
      } else if (meta.valid_until < Date.now()) {
        state.cacheData.delete(JSON.stringify(key))
        return
      }
      return meta.value
    },
  },

  actions: {
    writeCache() {
      // const serialized = JSON.stringify(Array.from(this.cacheData.entries()))
      const serialized = Object.fromEntries(this.cacheData.entries())
      SessionStorage.set("CacheStorage", stringify(serialized))
    },
    readCache() {
      return readCache()
    },
    setCached(key: CacheKey, value: CacheValue, ttl = DEFAULT_TIMEOUT) {
      const meta: CacheMeta = {
        value: value,
        valid_until: Date.now() + ttl,
      }
      this.cacheData.set(JSON.stringify(key), meta)
      this.writeCache()

      if (Date.now() - this.lastCleared > UPDATE_CLEARED_TIMEOUT) {
        this.clearOutdated()
        this.lastCleared = Date.now()
      }
    },
    delCached(key: CacheKey) {
      this.cacheData.delete(JSON.stringify(key))
      this.writeCache()
    },
    clearOutdated() {
      const now = Date.now()
      console.debug("[Cache] clearing outdated cache...")
      const sizeBefore = this.cacheData.size
      this.cacheData.forEach((value: CacheMeta, key: string) => {
        if (value.valid_until < now) {
          this.cacheData.delete(key)
        }
      })
      const sizeAfter = this.cacheData.size
      console.debug(`[Cache] cleared: (${sizeBefore} -> ${sizeAfter})`)
      if (sizeAfter != sizeBefore) {
        this.writeCache()
      }
    },

    // Helpers

    saveRecipe(recipe: RecipeRead) {
      this.setCached({ recipe: recipe.id }, recipe)
    },
    deleteRecipe(recipe: RecipeRead) {
      this.delCached({ recipe: recipe.id })
    },
  },
})
