import { defineStore } from "pinia"
import { LocalStorage } from "quasar"
import { RecipeShort } from "src/client"

const recipesSelectedDefault = LocalStorage.getItem("planRecipesSelected") as RecipeShort[]

export const useLocalStore = defineStore("local", {
  state: () => ({
    recipesSelected: recipesSelectedDefault ?? [],
  }),

  getters: {},

  actions: {
    recipesSelectedSave() {
      LocalStorage.set("planRecipesSelected", this.recipesSelected)
    },
    recipesSelectedIdx(recipe: RecipeShort) {
      const existIdx = this.recipesSelected.findIndex((el) => el.id == recipe.id)
      return existIdx
    },
    recipesSelectedAdd(recipe: RecipeShort) {
      console.debug("Add recipe: ", recipe)
      if (recipe) {
        const existIdx = this.recipesSelectedIdx(recipe)
        if (existIdx === -1) {
          this.recipesSelected.push(recipe)
          this.recipesSelectedSave()
        }
      }
    },
    recipesSelectedRemove(recipe: RecipeShort) {
      if (recipe) {
        const existIdx = this.recipesSelectedIdx(recipe)
        if (existIdx !== -1) {
          this.recipesSelected.splice(existIdx, 1)
        }
      }
    },
  },
})
