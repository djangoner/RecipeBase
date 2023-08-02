<template>
  <q-page
    class="q-pt-sm"
    padding
  >
    <!-- Compilations tabs -->
    <q-tabs
      v-model="compilation"
      content-class="text-grey-9"
      active-class="text-secondary"
    >
      <q-tab
        name=""
        icon="restaurant_menu"
        label="Все"
      />
      <q-tab
        name="new"
        icon="hourglass_top"
        label="Новое"
      />
      <q-tab
        name="top10"
        icon="grade"
        label="Топ 10"
      />
      <q-tab
        name="long_uncooked"
        icon="history"
        label="4+ недели"
      />
      <q-tab
        name="vlong_uncooked"
        icon="history"
        label="8+ недель"
      />
      <q-tab
        name="archive"
        icon="archive"
        label="Архив"
      />
    </q-tabs>

    <!-- Search input -->
    <q-input
      v-model="search"
      debounce="250"
      label="Поиск"
      autofocus
      clearable
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>
    <q-select
      v-model="ordering"
      :options="orderingOptions"
      label="Сортировка"
      map-options
      emit-value
      options-dense
      dense
    />

    <div class="row q-gutter-x-md items-center">
      <q-btn
        v-if="storeAuth.hasPerm('recipes.add_recipe')"
        class="q-my-sm"
        icon="add"
        color="secondary"
        size="sm"
        unelevated
        @click="openRecipe('new')"
      >
        Добавить рецепт
      </q-btn>
      <q-btn
        class="q-my-sm"
        icon="tune"
        color="primary"
        size="sm"
        unelevated
        @click="showFilters = !showFilters"
      >
        Фильтры
      </q-btn>

      <q-space />

      <q-btn-toggle
        v-model="displayMode"
        :options="[
          { label: 'Карточки', value: 'cards', icon: 'dashboard' },
          { label: 'Таблица', value: 'table', icon: 'table_view' },
        ]"
        toggle-color="primary"
        size="sm"
        dense
      />
    </div>

    <div
      v-if="recipes"
      class="q-my-sm"
    >
      Найдено результатов: {{ tablePagination?.rowsNumber }}
    </div>

    <!-- Recipe cards -->
    <div
      class="row q-col-gutter-x-md q-col-gutter-y-md"
      :class="$q.screen.gt.sm ? 'no-wrap' : ''"
    >
      <div
        v-if="recipes"
        class="col q-mt-md"
      >
        <!-- Cards mode -->
        <template v-if="displayMode == 'cards'">
          <!-- Pagination -->
          <div v-if="totalPages">
            <div class="flex justify-center q-mb-md">
              <q-pagination
                v-model="page"
                :max="totalPages"
                direction-links
              />
            </div>
            <q-separator class="q-my-md" />
            <!-- /Pagination -->
          </div>
          <div class="recipes-row row q-col-gutter-x-md q-col-gutter-y-sm">
            <div
              v-for="recipe of recipes"
              :key="recipe.id"
              class="col-xs-12 col-sm-6 col-md-4 col-lg-2"
            >
              <!-- Recipe card -->
              <recipe-card
                :recipe="recipe"
                @update-item="loadRecipes()"
              />
            </div>
          </div>

          <q-separator class="q-my-md" />

          <!-- Pagination -->
          <div
            v-if="recipes.length > 0 && totalPages"
            class="flex justify-center q-mt-md"
          >
            <q-pagination
              v-model="page"
              :max="totalPages"
              direction-links
            />
          </div>
          <!-- /Pagination -->
          <div
            v-else
            class="flex justify-center items-center full-height"
          >
            <h6 class="text-bold">
              Результатов не найдено
            </h6>
          </div>
        </template>
        <!-- Table mode -->
        <template v-else-if="displayMode == 'table'">
          <q-table
            v-model:pagination="tablePagination"
            title="Рецепты"
            :rows="recipes"
            :columns="tableColumns"
            :loading="loading"
            :filter="search"
            :rows-per-page-options="[1, 5, 10, 15, 20, 50]"
            binary-state-sort
            :dense="$q.screen.lt.md"
            @row-click="onRowClick"
            @request="loadRecipesTable"
          />
        </template>
      </div>

      <!-- Aside filters -->
      <transition
        appear
        enter-active-class="animated slideInRight"
        leave-active-class="animated slideOutRight"
      >
        <div
          v-if="showFilters && recipes"
          class="col-12 col-md-3 col-lg-2 col-shrink"
          :class="$q.screen.gt.sm ? '' : 'order-first'"
        >
          <q-card class="position-sticky shadow-1">
            <q-card-section>
              <h6 class="q-my-sm text-center text-bold">
                Фильтры
              </h6>

              <recipes-list-filters
                v-model="filters"
                @submit="loadRecipes()"
                @reset="resetFilters()"
              />
            </q-card-section>
          </q-card>
        </div>
      </transition>

      <q-inner-loading
        v-if="displayMode == 'cards'"
        :showing="loading"
      />
    </div>
  </q-page>
</template>

<script lang="ts">
import RecipesListFilters from "../components/Recipes/RecipesListFilters.vue"
import { useQuery } from "@oarepo/vue-query-synchronizer"
import recipeCard from "components/RecipeCard.vue"
import { date, debounce, QTableProps, SessionStorage } from "quasar"
import { PaginatedRecipeReadList, RecipeRead } from "src/client"
import { RecipesFilters, TablePagination, TablePropsOnRequest } from "src/modules/Globals"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { clearPayload } from "src/modules/Utils"
import { useAuthStore } from "src/stores/auth"
import { useBaseStore } from "src/stores/base.js"
import { defineComponent } from "vue"

const orderingOptions = [
  { label: "Кол-во приготовлений - по возрастанию", value: "cooked_times" },
  { label: "Кол-во приготовлений - по убыванию", value: "-cooked_times" },
  { label: "Создан - по возрастанию", value: "created" },
  { label: "Создан - по убыванию", value: "-created" },
  { label: "Последнее приготовление - по возрастанию", value: "last_cooked" },
  { label: "Последнее приготовление - по убыванию", value: "-last_cooked" },
  { label: "Цена - по возрастанию", value: "price_part" },
  { label: "Цена - по убыванию", value: "-price_part" },
  { label: "Полная цена - по возрастанию", value: "price_full" },
  { label: "Полная цена - по убыванию", value: "-price_full" },
  { label: "Название - по возрастанию", value: "title" },
  { label: "Название - по убыванию", value: "-title" },
]

const tableColumns = [
  {
    name: "title",
    label: "Название",
    align: "left",
    field: "title",
    required: true,
    sortable: true,
  },
  // {
  //   name: 'portion_count',
  //   label: 'Порций',
  //   field: 'portion_count',
  //   required: true,
  //   sortable: true,
  // },
  {
    name: "cooking_time",
    label: "Время",
    field: "cooking_time",
    required: true,
    sortable: true,
    style: "width: 40px",
  },
  {
    name: "last_cooked",
    label: "Приготовили",
    field: (r: RecipeRead) => date.formatDate(r.last_cooked, "YYYY.MM.DD"),
    required: true,
    sortable: true,
    style: "width: 40px",
  },
  {
    name: "created",
    label: "Создан",
    field: (r: RecipeRead) => (r.created ? date.formatDate(r.created, "YYYY.MM.DD hh:mm") : ""),
    required: true,
    sortable: true,
    style: "width: 50px",
  },
] as QTableProps["columns"]

interface QueryInterface {
  compilation?: string
  display: string
}

const defaultFilters = {
  cooking_time: { min: 5, max: 120 },
  price: { min: 0, max: 1000 },
  difficulty: {min: 1, max: 5},
  priceUseFull: false,
  tags_include: [],
  tags_exclude: [],
  ingredients_include: [],
  ingredients_exclude: [],
  ratings: {},
} as RecipesFilters

export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { recipeCard, RecipesListFilters },
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore()
    const storeAuth = useAuthStore()

    // eslint-disable-next-line @typescript-eslint/no-empty-function
    const emptyFunc = () => {}

    const reset = Boolean(this.$route.query.reset)

    const initialFilters = reset ? defaultFilters : SessionStorage.getItem("recipesFilters") as RecipesFilters || defaultFilters

    const searchTag = this.$route.query.q_tag
    if (searchTag){
      initialFilters.tags_include.push(Number(searchTag))
    }

    return {
      store,
      $query: useQuery(),
      storeAuth,
      search: SessionStorage.getItem("recipesSearch") ?? "",
      page: 1,
      page_size: 20,
      loading: false,
      ordering: SessionStorage.getItem("recipesOrdering") ?? "-cooked_times",
      tablePagination: {
        rowsPerPage: 20,
        page: 1,
        sortBy: "created",
        descending: true,
      } as TablePagination,
      // compilation: this.$query.compilation,
      showFilters: this.$q.localStorage.getItem("recipesShowFilters"),
      filters: Object.assign({}, initialFilters) ,
      filtersDefault: JSON.parse(JSON.stringify(defaultFilters)) as RecipesFilters,
      orderingOptions,
      debounceLoadRecipes: emptyFunc,
    }
  },

  computed: {
    recipes() {
      return this.store.recipes
    },
    compilation: {
      get() {
        return (this.$query as unknown as QueryInterface).compilation
      },
      set(val: string) {
        ;(this.$query as unknown as QueryInterface).compilation = val
      },
    },
    displayMode: {
      get() {
        return (this.$query as unknown as QueryInterface).display
      },
      set(val: string) {
        ;(this.$query as unknown as QueryInterface).display = val
      },
    },
    totalPages(): number | null {
      if (!this.tablePagination.rowsNumber || !this.tablePagination.rowsPerPage) {
        return null
      }
      return Math.ceil(this.tablePagination?.rowsNumber / this.tablePagination?.rowsPerPage) || 1
    },
    tableColumns() {
      let r = tableColumns?.slice() || []
      if (this.compilation == "top10") {
        r.unshift({
          name: "pos",
          label: "#",
          field: (r: RecipeRead) => (this.recipes ? String(this.recipes.indexOf(r) + 1 + (this.page - 1) * this.page_size) : "-"),
          style: "width: 20px",
          sortable: false,
          required: false,
        })
        r.splice(2, 0, {
          name: "cooked_times",
          label: "Кол-во",
          field: "cooked_times",
          style: "width: 20px",
          sortable: true,
          required: false,
        })
      } else if (this.compilation == "new") {
        r = r.filter((c) => c.name !== "last_cooked")
      }
      return r
    },
  },

  watch: {
    search(val: string) {
      this.page = 1
      void this.loadRecipes()
      SessionStorage.set("recipesSearch", val)
    },
    ordering(val: boolean) {
      void this.loadRecipes()
      SessionStorage.set("recipesOrdering", val)
    },
    compilation() {
      this.page = 1
      void this.loadRecipes()
    },
    page() {
      void this.loadRecipes()
    },
    filters: {
      deep: true,
      handler(val) {
        SessionStorage.set("recipesFilters", val)
        this.page = 1
        this.debounceLoadRecipes()
      },
    },
    showFilters(val) {
      this.$q.localStorage.set("recipesShowFilters", val)
    },
  },
  created() {
    // eslint-disable-next-line @typescript-eslint/unbound-method
    this.debounceLoadRecipes = debounce(this.loadRecipes, 1000)
    void this.$nextTick(() => {
      void this.loadRecipes()
    })
  },

  methods: {
    loadRecipes() {
      return new Promise((resolve, reject) => {
        const payload = {
          omit: "content,content_source,recommendations_ingredients,recommendations_recipes,recommendations_tags",
        } as { [key: string]: string }

        payload.search = this.search
        payload.page = String(this.page)
        payload.pageSize = String(this.page_size)

        if (this.compilation == "top10") {
          payload.ordering = ""
          if (this.tablePagination.sortBy !== "cooked_times") {
            this.tablePagination.sortBy = "cooked_times"
            this.tablePagination.descending = true
          }
        } else {
          payload.ordering = this.ordering
          this.tablePagination.sortBy = this.ordering
        }
        // Compilation
        if (this.compilation) {
          payload.compilation = this.compilation
        }
        // Tags
        if (this.filters.tags_include) {
          payload.tagsInclude = this.filters.tags_include.join(",")
        }
        if (this.filters.tags_exclude) {
          payload.tagsExclude = this.filters.tags_exclude.join(",")
        }
        // Tags
        if (this.filters.ingredients_include) {
          payload.ingredientsInclude = this.filters.ingredients_include.join(",")
        }
        if (this.filters.ingredients_exclude) {
          payload.ingredientsExclude = this.filters.ingredients_exclude.join(",")
        }

        // Cooking time
        if (this.filters.cooking_time) {
          if (this.filters.cooking_time.min > defaultFilters.cooking_time.min) {
            payload.cookingTimeGt = String(this.filters.cooking_time.min)
          }
          if (this.filters.cooking_time.max < defaultFilters.cooking_time.max) {
            payload.cookingTimeLt = String(this.filters.cooking_time.max)
          }
        }
        if (this.filters.price) {
          if (this.filters.price.min > defaultFilters.price.min) {
            payload[this.filters.priceUseFull ? "priceFullGt" : "pricePartGt"] = String(this.filters.price.min)
          }
          if (this.filters.price.max < defaultFilters.price.max) {
            payload[this.filters.priceUseFull ? "priceFullLt" : "pricePartLt"] = String(this.filters.price.max)
          }
        }
        // Difficulty
        if (this.filters.difficulty) {
          if (this.filters.difficulty.min > defaultFilters.difficulty.min) {
            payload.difficultyGt = String(this.filters.difficulty.min)
          }
          if (this.filters.difficulty.max < defaultFilters.difficulty.max) {
            payload.difficultyLt = String(this.filters.difficulty.max)
          }
        }

        // Ratings
        if (this.filters.ratings) {
          const r = []
          for (const [user_id, values] of Object.entries(this.filters.ratings)) {
            if (values.min == values.max) {
              r.push(`${user_id}_${values.min}`)
              // payload.rating = `${user_id}_${values.min}`;
            } else {
              if (values.min > 0) {
                r.push(`${user_id}_+${values.min}`)
                // payload.rating = `${user_id}_+${values.min}`;
              }

              if (values.max < 5) {
                r.push(`${user_id}_-${values.max}`)
                // payload.rating = `${user_id}_-${values.max}`;
              }
            }
          }
          payload.rating = r.join(",")
        }

        // Send request

        this.loading = true

        this.store
          .loadRecipes(clearPayload(payload))
          .then((resp: PaginatedRecipeReadList) => {
            this.loading = false
            this.tablePagination.rowsNumber = resp?.count
            resolve(resp)
          })
          .catch((err: CustomAxiosError) => {
            console.warn(err)
            reject(err)
            this.loading = false
            this.handleErrors(err, "Ошибка загрузки рецептов")
          })
      })
    },
    loadRecipesTable(props: TablePropsOnRequest) {
      console.debug("tableProps: ", props.pagination)
      this.ordering = props?.pagination?.descending && !props?.pagination?.sortBy?.startsWith("-") ? "-" : ""
      this.ordering += props?.pagination?.sortBy
      this.page = props?.pagination?.page || 1
      this.page_size = props?.pagination?.rowsPerPage || 20
      void this.loadRecipes().then(() => {
        Object.assign(this.tablePagination, props.pagination)
      })
    },
    onRowClick(e: Event, row: RecipeRead) {
      this.openRecipe(row.id)
    },
    resetFilters() {
      this.filters = Object.assign({}, this.filtersDefault)
      this.filters.ratings = []
      console.debug("Reset: ", this.filters)
    },
    openRecipe(id: number | "new") {
      void this.$router.push({ name: "recipe", params: { id: id } })
    },
  },
})
</script>

<style lang="scss" scoped>
.position-sticky {
  position: sticky;
  top: 60px;
}
</style>
