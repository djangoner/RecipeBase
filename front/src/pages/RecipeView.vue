<template>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-pb-md">
      <div>
        <q-btn
          icon="arrow_back"
          size="sm"
          color="grey"
          @click="$router.go(-1)"
        >
          Назад
        </q-btn>
      </div>
      <div v-if="!edit">
        <q-btn
          v-if="storeAuth.hasPerm('recipes.add_recipe')"
          icon="add"
          size="sm"
          color="positive"
          @click="$router.push({ name: 'recipe', params: { id: 'new' } })"
        >
          Новый рецепт
        </q-btn>
      </div>
    </div>

    <q-form
      class="q-mt-md"
      @submit.prevent="saveRecipe()"
    >
      <div
        v-if="recipe"
        class="row q-col-gutter-y-lg q-col-gutter-x-md"
      >
        <div class="col-xs-12 col-md-6">
          <!--  col-lg-8 -->
          <q-card class="shadow-1">
            <q-card-section
              class="flex column"
              :class="dense ? 'q-gutter-y-sm' : 'q-gutter-y-md'"
            >
              <recipe-info-edit
                v-model="recipe"
                v-model:edit="edit"
              />

              <div class="flex q-col-gutter-md justify-around q-mt-md">
                <div>
                  <q-btn
                    v-if="edit"
                    type="submit"
                    icon="save"
                    color="positive"
                    :loading="saving"
                    no-caps
                    unelevated
                    @click="saveAndContinue = false"
                  >
                    Сохранить
                  </q-btn>
                </div>
                <div>
                  <q-btn
                    v-if="edit"
                    type="submit"
                    icon="save"
                    color="positive"
                    :loading="saving"
                    no-caps
                    unelevated
                    @click="saveAndContinue = true"
                  >
                    Сохранить и продолжить
                  </q-btn>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-xs-12 col-md-6 q-gutter-y-sm">
          <!--  col-lg-4 -->
          <!-- Aside information -->
          <q-card class="q-mt-none position-sticky shadow-1">
            <q-card-section>
              <recipe-info :recipe="recipe" />
              <recipe-prices :recipe="recipe" />
              <!-- Recommendations -->
              <q-expansion-item label="Рекомендации">
                <q-separator />
                <recipe-recommendations
                  v-model:recipe="recipe"
                  :edit="edit"
                />
                <q-separator />
              </q-expansion-item>
              <!-- Ingredients -->
              <recipe-ingredients
                v-model:recipe="recipe"
                :edit="edit"
              />

              <!-- Recipe Ratings -->

              <div class="q-my-sm">
                <div class="text-h6 text-center q-mb-sm">
                  Рейтинг:
                </div>

                <recipe-rating
                  v-if="store.recipe"
                  v-model="store.recipe"
                  :edit="edit"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-form>

    <q-inner-loading :showing="loading || saving" />
  </q-page>
</template>

<script lang="ts">
import RecipeRecommendations from '../components/Recipes/RecipeRecommendations.vue'
import RecipeInfoEdit from '../components/Recipes/RecipeInfoEdit.vue'

import RecipeIngredients from "../components/Recipes/RecipeIngredients.vue"
import RecipePrices from "../components/Recipes/RecipePrices.vue"
import RecipeInfo from "../components/Recipes/RecipeInfo.vue"
import { useBaseStore } from "src/stores/base"
import RecipeRating from "src/components/RecipeRating.vue"
import { defineComponent } from "vue"
import { RecipeImage, RecipeIngredientRead, RecipeRead } from "src/client"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { AmountTypesConvert, AmountTypesTypes } from "src/modules/Globals"
import { RecipeFromRead } from "src/Convert"
import { useAuthStore } from "src/stores/auth"
import {dateFormat, dateTimeFormat } from "src/modules/Utils"

const defaultRecipe = {
  content_source: "",
  content: "",
  tags: [],
  images: [],
  ingredients: [],
  ratings: [],
  portion_count: null,
  preparation_time: null,
  is_archived: false,
}

interface PatchedRecipeRead {
  content: string
  content_source: string
  images: RecipeImage[]
}

export default defineComponent({
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeRating,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeInfo,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipePrices,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeIngredients,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeInfoEdit, RecipeRecommendations
  },
  mixins: [HandleErrorsMixin],
  beforeRouteUpdate(to) {
    if (to.params.id == "new") {
      this.loadRecipe("new")
    } else {
      this.loadRecipe(parseInt(to.params?.id as string))
    }
  },
  data() {
    const store = useBaseStore()
    const storeAuth = useAuthStore()

    return {
      store,
      storeAuth,
      loading: false,
      saving: false,
      edit: false,
      saveAndContinue: false,
    }
  },

  computed: {
    recipe: {
      get() {
        return this.store.recipe as (RecipeRead & PatchedRecipeRead) | null
      },
      set(val: RecipeRead & PatchedRecipeRead) {
        this.store.recipe = val
      },
    },
    ingredients() {
      return this.store.ingredients
    },
    exists() {
      return Boolean(this.recipe?.id)
    },
    dense() {
      // return this.$q.screen.lt.sm;
      return true
    },
    amount_types() {
      return this.store.amount_types
    },
    amountTypeList() {
      return this.amount_types?.types as AmountTypesTypes
    },
    amountTypeConvert() {
      return this.amount_types?.convert as AmountTypesConvert
    },
  },

  watch: {
    "recipe.ingredients": {
      deep: true,
      handler(val: RecipeIngredientRead[]) {
        if (!this.edit || !val) return
        this.calculateIngredientsGrams()
      },
    },
  },
  created() {
    this.loadRecipe()
  },
  methods: {
    dateFormat,
    dateTimeFormat,
    loadRecipe(load_id?: number | "new" | undefined) {
      let id: string | number | "new" = load_id || (this.$route.params.id as string)

      if (id == "new") {
        this.resetData()
        this.edit = true
        return
      } else {
        this.edit = false
      }

      if (typeof id == "string") {
        id = parseInt(id)
      }

      this.loading = true

      this.store
        .loadRecipe(id)
        .then(() => {
          this.loading = false
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки рецептов")
        })
    },
    resetData() {
      console.debug("Recipe resetData")
      // @ts-expect-error: Default recipe not full
      this.store.recipe = Object.assign({}, defaultRecipe)
      // this.recipe = Object.assign({}, defaultRecipe);
      if (this.recipe?.tags) {
        this.recipe.tags.length = 0
      }
      if (this.recipe?.ingredients) {
        this.recipe.ingredients.length = 0
      }
    },
    async uploadImg(img: RecipeImage): Promise<RecipeImage> {
      return new Promise((resolve, reject) => {
        if (!this.recipe) {
          reject()
        }
        // let formData = new FormData();
        // formData.append('recipe', String(this.recipe?.id as number));
        // formData.append('image', img.image);
        // formData.append('title', img.title as string);
        // formData.append('num', String(img.num));
        const payload = {
          recipe: String(this.recipe?.id as number),
          image: img.image,
          title: img.title as string,
          num: String(img.num),
        }

        this.store
          // @ts-expect-error: Recipe image will be created
          .createRecipeImage(payload)
          .then((resp) => {
            resolve(resp)
            console.debug("IMG: ", resp)
          })
          .catch((err) => reject(err))
      })
    },
    async handleImages(images_src: RecipeImage[]) {
      const images = await Promise.all(
        images_src.map(async (i) => {
          // console.debug('Image upload: ', i, Boolean(i.upload_preview), Boolean(i.id));
          // @ts-expect-error: Upload preview generation
          if (i.upload_preview) {
            const res = await this.uploadImg(i)
            // (async () => {
            // await ...
            // })();
            console.debug("IMG uploaded: ", res, i)

            Object.assign(i, res)
            // delete res['image'];
          }
          if (i.id) {
            // @ts-expect-error readonly image
            delete i["image"]
          }
          return i
        })
      )
      return images
    },
    async saveRecipe() {
      // console.debug('Save recipe');
      this.saving = true
      if (!this.saveAndContinue) {
        this.edit = false
      }
      const payload = RecipeFromRead(this.recipe)
      const isCreating = !this.exists
      const method = isCreating ? this.store.createRecipe : this.store.saveRecipe

      if (isCreating) {
        payload.images = []
      } else {
        payload.images = await this.handleImages(payload.images as RecipeImage[])
      }

      console.debug("Saving recipe: ", payload)

      method(payload)
        .then((resp) => {
          this.saving = false

          if (isCreating) {
            console.debug("Redirecting from created recipe: ", resp)
            void this.$router.replace({
              name: "recipe",
              params: { id: resp.id },
            })
            // .catch(() => {});
          }

          const created_tx = isCreating ? "создан" : "сохранен"
          this.$q.notify({
            type: "positive",
            message: `Рецепт успешно ${created_tx}`,
          })
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false
          this.edit = true
          this.handleErrors(err, "Ошибка сохранения рецепта")
        })
    },
    calculateIngredientsGrams() {
      if (!this.edit || !this.amountTypeConvert) return
      this.recipe?.ingredients?.map((i) => {
        if (!this.amountTypeConvert) return i
        const coef = this.amountTypeConvert[i.amount_type || "g"]
        let newGrams = 0
        if (coef) {
          newGrams = i.amount * coef
        } else if (i.amount_type == "items" && i.ingredient.item_weight) {
          newGrams = i.amount * i.ingredient.item_weight
        }
        // @ts-expect-error Pre-compute ingredient grams
        i.amount_grams = Math.round(newGrams * 100) / 100
        // console.debug("Ing: ", i);
        return i
      })
      // console.debug("Calculating grams...");
    },
  },
})
</script>

<style lang="scss" scoped>
.position-sticky {
  position: sticky;
  top: 60px;
}

:deep(.recipe-text) {
  overflow: hidden;
  word-break: break-word;

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 120%;
  }
  h1 {
    font-size: 2.5rem;
    font-weight: bold;
  }
  h2 {
    font-size: 2rem;
    font-weight: bold;
  }
  h3 {
    font-size: 1.5rem;
  }
  h4,
  h5,
  h6 {
    font-size: 1rem;
  }

  img {
    max-width: 100%;
  }
}
.format-spaces {
  white-space: pre-line;
}
:deep(.no-bottom) {
  .q-table__bottom {
    display: none;
    min-height: 0;
  }
}
</style>
