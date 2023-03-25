<template>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-pb-md">
      <div>
        <q-btn
          icon="arrow_back"
          size="sm"
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
          <q-card>
            <q-card-section
              class="flex column"
              :class="dense ? 'q-gutter-y-sm' : 'q-gutter-y-md'"
            >
              <!-- Recipe details -->
              <div class="q-mt-none">
                <q-input
                  v-if="edit"
                  v-model="recipe.title"
                  label="Название рецепта *"
                  :rules="[requiredRule]"
                  filled
                  :dense="dense"
                >
                  <template #after>
                    <q-btn
                      v-if="exists && storeAuth.hasPerm('recipes.change_recipe')"
                      icon="edit"
                      flat
                      @click="toggleEdit()"
                    >
                      <q-tooltip>Предпросмотр рецепта (изменения не будут применены!)</q-tooltip>
                    </q-btn>
                  </template>
                </q-input>
                <h4
                  v-else
                  class="text-center q-my-none"
                >
                  <q-icon
                    v-if="recipe.is_archived"
                    class="q-mr-xs"
                    name="archive"
                    size="sm"
                    color="primary"
                  >
                    <q-tooltip>Этот рецепт архивирован</q-tooltip>
                  </q-icon>
                  {{ recipe.title }}
                  <q-btn
                    v-if="storeAuth.hasPerm('recipes.change_recipe')"
                    icon="edit"
                    flat
                    @click="toggleEdit()"
                  >
                    <q-tooltip>Изменить рецепт</q-tooltip>
                  </q-btn>

                  <recipe-menu :recipe="recipe" />
                </h4>
              </div>

              <!-- Recipe source -->
              <div>
                <q-input
                  v-if="edit"
                  v-model="recipe.source_link"
                  label="Источник рецепта"
                  filled
                  :dense="dense"
                />
                <h6
                  v-else
                  class="text-center q-my-none"
                >
                  <q-btn
                    v-if="recipe.source_link && recipe.source_link.startsWith('http')"
                    :href="recipe.source_link"
                    target="_blank"
                    icon="open_in_new"
                    size="sm"
                  >
                    Открыть источник
                  </q-btn>
                  <h6
                    v-else
                    class="text-center q-my-none"
                  >
                    Источник: {{ recipe.source_link || "-" }}
                  </h6>
                </h6>
              </div>

              <!-- Recipe tags -->
              <div class="row recipe-tags items-center q-gutter-x-md">
                <span class="text-subtitle2">Метки: </span>
                <q-chip
                  v-for="tag of recipe.tags"
                  :key="tag.id"
                  class="cursor-pointer"
                  :removable="edit"
                  @remove="removeTag(tag)"
                >
                  {{ tag.title }}
                </q-chip>

                <q-select
                  v-if="edit && tags"
                  v-model="tagAddSelect"
                  label="Добавить метку"
                  keydown.enter.prevent="addTag()"
                  :input-debounce="0"
                  :options="tagList || []"
                  :options-dense="dense"
                  :dense="dense"
                  option-label="title"
                  use-input
                  new-value-mode="add-unique"
                  @filter="filterTags"
                  @new-value="addNewTag"
                >
                  <template #no-option>
                    <q-item>
                      <q-item-section class="text-grey">
                        Нет результатов
                      </q-item-section>
                    </q-item>
                  </template>
                  <template #after>
                    <q-btn
                      icon="add"
                      size="sm"
                      color="positive"
                      @click="addTag()"
                    />
                  </template>
                </q-select>
              </div>

              <!-- Info -->

              <div>
                <q-input
                  v-if="edit"
                  v-model.number="recipe.portion_count"
                  type="number"
                  label="Количество порций"
                  filled
                  :dense="dense"
                />
                <h6
                  v-else-if="recipe.portion_count"
                  class="text-center q-my-none"
                >
                  <q-icon
                    name="pie_chart_outline"
                    color="grey"
                  />
                  Порций: {{ recipe.portion_count || "-" }}
                </h6>
              </div>
              <div>
                <q-input
                  v-if="edit"
                  v-model.number="recipe.cooking_time"
                  type="number"
                  label="Время приготовления"
                  hint="Примерное время приготовления в минутах"
                  filled
                  :dense="dense"
                />
                <h6
                  v-else-if="recipe.cooking_time"
                  class="text-center q-my-none"
                >
                  <q-icon
                    name="timer"
                    color="grey"
                  />
                  Время приготовления: {{ recipe.cooking_time || "-" }}
                </h6>
              </div>
              <div>
                <q-input
                  v-if="edit"
                  v-model.number="recipe.preparation_time"
                  type="number"
                  label="Время подготовки"
                  hint="Примерное время подготовки к приготовлению в минутах. Например: настаивание теста, размачивание нута итп."
                  filled
                  :dense="dense"
                />
                <h6
                  v-else-if="recipe.preparation_time"
                  class="text-center q-my-none"
                >
                  <q-icon
                    name="timer"
                    color="grey"
                  />
                  Время подготовки: {{ recipe.preparation_time || "-" }}
                </h6>
              </div>
              <div v-if="edit">
                <q-select
                  v-model="recipe.is_archived"
                  :options="archivedOptions"
                  label="Статус"
                  options-dense
                  map-options
                  emit-value
                  filled
                  :dense="dense"
                />
              </div>

              <!-- Images carousel -->
              <div
                v-if="!edit"
                class="images-carousel q-py-md"
              >
                <q-carousel
                  v-if="(recipe.images || [])?.length > 0"
                  v-model="slide"
                  v-model:fullscreen="fullscreen"
                  :autoplay="autoplay"
                  :height="$q.screen.gt.md ? '450px' : '250px'"
                  transition-prev="slide-right"
                  transition-next="slide-left"
                  animated
                  navigation
                  infinite
                  arrows
                  @mouseenter="autoplay = false"
                  @mouseleave="autoplay = true"
                >
                  <template #control>
                    <q-carousel-control
                      position="bottom-right"
                      :offset="[18, 18]"
                    >
                      <q-btn
                        push
                        round
                        dense
                        color="white"
                        text-color="primary"
                        :icon="fullscreen ? 'fullscreen_exit' : 'fullscreen'"
                        @click="fullscreen = !fullscreen"
                      />
                    </q-carousel-control>
                  </template>
                  <q-carousel-slide
                    v-for="(img, idx) of recipe.images"
                    :key="img.id"
                    :name="idx + 1"
                    :img-src="img.image"
                  />
                </q-carousel>
              </div>

              <recipe-images-upload
                v-if="edit && exists"
                v-model="recipe.images"
              />
              <q-separator />

              <!-- Recipe content -->

              <div
                v-if="edit"
                class="q-py-md q-gutter-sm full-width"
              >
                <h6 class="q-my-sm">
                  Содержание (изначальное, источник)
                </h6>
                <q-editor
                  v-model="recipe.content_source"
                  :dense="$q.screen.lt.md"
                  :toolbar="editorToolbar"
                  :fonts="editorFonts"
                />
                <h6 class="q-my-sm">
                  Содержание (редактированное)
                </h6>
                <q-editor
                  v-model="recipe.content"
                  :dense="$q.screen.lt.md"
                  :toolbar="editorToolbar"
                  :fonts="editorFonts"
                />

                <h6 class="q-my-sm">
                  Комментарий
                </h6>
                <q-input
                  v-model="recipe.comment"
                  type="textarea"
                  label="Комментарий"
                />
              </div>
              <div v-else>
                <div v-if="recipe.content_source">
                  <span class="text-h6 q-my-sm text-primary">Содержание (изначальное)</span>
                  <div
                    class="recipe-text"
                    v-html="recipe.content_source"
                  />
                  <q-separator />
                </div>

                <div v-if="recipe.content">
                  <span class="text-h6 q-my-sm text-primary">Содержание</span>

                  <div
                    class="recipe-text"
                    v-html="recipe.content"
                  />
                  <q-separator />
                </div>
              </div>
              <q-input
                v-model="recipe.short_description"
                type="textarea"
                label="Короткое описание"
                hint="Показывается на карточке рецепта"
                :readonly="!edit"
              />
              <div v-if="!edit && recipe.comment">
                <span class="text-h6 q-my-sm text-primary">Комментарий</span>

                <div
                  class="recipe-text format-spaces"
                  v-html="recipe.comment"
                />
                <q-separator />
              </div>

              <div class="flex q-col-gutter-md justify-around q-mt-md">
                <div>
                  <q-btn
                    v-if="edit"
                    type="submit"
                    icon="save"
                    color="positive"
                    :loading="saving"
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
          <q-card class="q-mt-none position-sticky">
            <q-card-section>
              <recipe-info :recipe="recipe" />
              <recipe-prices :recipe="recipe" />
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
import RecipeIngredients from "../components/Recipes/RecipeIngredients.vue"
import RecipePrices from "../components/Recipes/RecipePrices.vue"
import RecipeInfo from "../components/Recipes/RecipeInfo.vue"
import { useBaseStore } from "src/stores/base"
import { date } from "quasar"
import RecipeImagesUpload from "src/components/RecipeImagesUpload.vue"
import RecipeRating from "src/components/RecipeRating.vue"
import RecipeMenu from "src/components/RecipeMenu.vue"
import { defineComponent } from "vue"
import { IngredientRead, RecipeImage, RecipeIngredientRead, RecipeRead, RecipeTag } from "src/client"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { AmountTypesConvert, AmountTypesTypes } from "src/modules/Globals"
import { RecipeFromRead } from "src/Convert"
import { useAuthStore } from "src/stores/auth"

const defaultRecipe = {
  content_source: "",
  content: "",
  tags: [],
  images: [],
  ingredients: [],
  ratings: [],
  portion_count: null,
  preparation_time: null,
}

interface PatchedRecipeRead {
  content: string
  content_source: string
  images: RecipeImage[]
}

export default defineComponent({
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeImagesUpload,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeRating,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeMenu,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeInfo,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipePrices,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeIngredients,
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

    const ingredientsColumns = [
      {
        name: "title",
        label: "Название",
        field: (row: RecipeIngredientRead) => row.ingredient?.title,
        required: true,
        sortable: true,
        style: "width: 50px",
      },
      // {
      //   name: 'amount_type',
      //   label: 'Ед. изм.',
      //   field: (row) => row.amount_type,
      //   required: true,
      //   sortable: true,
      //   style: 'width: 20px',
      // },
      {
        name: "amount_rec",
        label: "Вес (рецепт)",
        field: (row: RecipeIngredientRead) => String(row.amount) + "  (" + row.amount_type_str + ")",
        required: true,
        sortable: true,
        style: "width: 20px",
      },
      {
        name: "amount_g",
        label: "Вес (гр.)",
        field: (row: RecipeIngredientRead) => (row.amount_grams ? String(row.amount_grams) + " гр." : "-"),
        required: true,
        sortable: true,
        style: "width: 30px",
      },
      {
        name: "is_main",
        label: "Основной",
        field: "is_main",
        required: true,
        sortable: true,
        style: "width: 30px",
      },
    ]

    const ingAddDefault = {
      select: null as { id: number | null; title: string } | null,
      amount: null,
      amount_type: "g",
      is_main: false,
    }

    const editorToolbar = [
      [
        {
          label: this.$q.lang.editor.align,
          icon: this.$q.iconSet.editor.align,
          fixedLabel: true,
          list: "only-icons",
          options: ["left", "center", "right", "justify"],
        },
        {
          label: this.$q.lang.editor.align,
          icon: this.$q.iconSet.editor.align,
          fixedLabel: true,
          options: ["left", "center", "right", "justify"],
        },
      ],
      ["bold", "italic", "strike", "underline", "subscript", "superscript"],
      ["token", "hr", "link", "custom_btn"],
      ["print", "fullscreen"],
      [
        {
          label: this.$q.lang.editor.formatting,
          icon: this.$q.iconSet.editor.formatting,
          list: "no-icons",
          options: ["p", "h1", "h2", "h3", "h4", "h5", "h6", "code"],
        },
        {
          label: this.$q.lang.editor.fontSize,
          icon: this.$q.iconSet.editor.fontSize,
          fixedLabel: true,
          fixedIcon: true,
          list: "no-icons",
          options: ["size-1", "size-2", "size-3", "size-4", "size-5", "size-6", "size-7"],
        },
        {
          label: this.$q.lang.editor.defaultFont,
          icon: this.$q.iconSet.editor.font,
          fixedIcon: true,
          list: "no-icons",
          options: ["default_font", "arial", "arial_black", "comic_sans", "courier_new", "impact", "lucida_grande", "times_new_roman", "verdana"],
        },
        "removeFormat",
      ],
      ["quote", "unordered", "ordered", "outdent", "indent"],

      ["undo", "redo"],
      ["viewsource"],
    ]

    const editorFonts = {
      arial: "Arial",
      arial_black: "Arial Black",
      comic_sans: "Comic Sans MS",
      courier_new: "Courier New",
      impact: "Impact",
      lucida_grande: "Lucida Grande",
      times_new_roman: "Times New Roman",
      verdana: "Verdana",
    }

    const requiredRule = (val: string | number) => !!val || "Обязательное поле"

    return {
      store,
      storeAuth,
      loading: false,
      saving: false,
      slide: 1,
      autoplay: true,
      fullscreen: false,
      edit: false,
      tagAddSelect: null as RecipeTag | null,
      tagList: null as RecipeTag[] | null,
      saveAndContinue: false,
      ingAddDefault,
      addIngredientSelect: null as IngredientRead | null,
      ingList: null as IngredientRead[] | null,
      requiredRule,
      ingredientsColumns,
      editorToolbar,
      editorFonts,
      archivedOptions: [
        { label: "Не архивирован", value: false },
        { label: "Архивирован", value: true },
      ],
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
    tags() {
      return this.store.tags
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
      return this.store.amount_types;
    },
    amountTypeList() {
      return this.amount_types?.types as AmountTypesTypes;
    },
    amountTypeConvert() {
      return this.amount_types?.convert as AmountTypesConvert;
    },
  },

  watch: {
    edit(val) {
      const column_actions = {
        name: "actions",
        label: "Действия",
        field: () => "",
        required: true,
        sortable: false,
        style: "width: 75px",
      }
      const column_amount_type = {
        name: "amount_type",
        label: "Единица измерения",
        field: () => "",
        required: true,
        sortable: false,
        style: "width: 120px",
      }

      if (val) {
        this.ingredientsColumns.push(column_actions)
        this.ingredientsColumns.splice(1, 0, column_amount_type)
      } else {
        this.ingredientsColumns = this.ingredientsColumns?.filter((i) => i.name !== column_actions.name && i.name !== column_amount_type.name)
      }
    },
    "recipe.ingredients": {
      deep: true,
      handler(val: RecipeIngredientRead[]) {
        if (!this.edit || !val) return
        this.calculateIngredientsGrams()
      },
    },
    tagAddSelect() {
      this.addTag()
    },
  },
  created() {
    this.loadRecipe()
    if (!this.tags) {
      this.loadTags()
    }
  },
  methods: {
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
    loadTags() {
      const payload = {
        pageSize: 1000,
      }
      this.store
        .loadTags(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, "Ошибка загрузки меток")
        })
    },
    toggleEdit() {
      this.edit = !this.edit
    },
    removeTag(tag: RecipeTag) {
      if (!this.recipe) {
        return
        }
      console.debug("Remove tag: ", tag)
      this.recipe.tags =
        this.recipe?.tags?.filter((t) => {
          return t.title !== tag.title
        }) || []
    },
    addTag() {
      console.debug("Add tag: ", this.tagAddSelect)
      if (!this.tagAddSelect) {
        return
      }
      this.recipe?.tags?.push(this.tagAddSelect)
      this.tagAddSelect = null
    },
    addNewTag(new_tag: string) {
      // , done: CallableFunction
      console.debug("Add new tag: ", new_tag)
      if (!new_tag) {
        return
      }
      const exists = this.recipe?.tags?.find((t) => t.title.toLowerCase() === new_tag.toLowerCase())
      if (exists) {
        // If tag with this name already added to recipe
        console.debug("Tag already exists!")
        return
      }

      const existsNotUsed = this.tags?.find((t) => t.title.toLowerCase() === new_tag.toLowerCase())
      if (existsNotUsed) {
        // If tag with this name exists in DB
        console.debug("Using existing tag in DB")
        this.tagAddSelect = existsNotUsed
        this.addTag()
        return
      }

      this.tagAddSelect = {
        // @ts-expect-error: Tag will be created
        id: null,
        title: new_tag,
      }
      // done(new_tag, 'add-unique');
      this.addTag()
    },
    filterTags(val: string, update: CallableFunction) {
      update(() => {
        const isUsed = (tag: RecipeTag) => {
          return this.recipe?.tags?.some((t) => t.id == tag.id)
        }

        const needle = val.toLowerCase()
        const tags = this.tags

        this.tagList = tags?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)) || []
        // console.debug(needle, this.tagList, tags);
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
    dateTimeFormat(raw: Date | string | null): string {
      if (!raw) {
        return "-"
      }
      return date.formatDate(raw, "YYYY.MM.DD hh:mm")
    },
    dateFormat(raw: Date | string): string {
      return date.formatDate(raw, "YYYY.MM.DD")
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
