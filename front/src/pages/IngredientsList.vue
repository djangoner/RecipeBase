<template>
  <q-page padding>
    <div
      class="row q-col-gutter-x-md q-col-gutter-y-md"
      :class="$q.screen.gt.sm ? 'no-wrap' : ''"
    >
      <div class="col">
        <q-table
          title="Ингредиенты"
          :rows="ingredients || []"
          :columns="tableColumns"
          :loading="loading"
          :filter="tableFilter"
          :rows-per-page-options="[1, 5, 10, 15, 20, 50, 100]"
          @row-click="onRowClick"
          v-model:pagination="tablePagination"
          @request="loadIngredients"
          binary-state-sort
          :dense="$q.screen.lt.md"
        >
          <!-- Search & create new -->
          <template v-slot:top-right>
            <q-btn
              v-if="storeAuth.hasPerm('recipes.add_ingredient')"
              class="q-mx-md"
              @click="
                $router.push({ name: 'ingredient', params: { id: 'new' } })
              "
              icon="add"
              size="sm"
              color="positive"
              >Новый ингредиент</q-btn
            >
            <q-btn
              icon="tune"
              color="primary"
              size="sm"
              @click="showFilters = !showFilters"
              >Фильтры</q-btn
            >
            <q-input
              class="q-ml-md"
              borderless
              dense
              debounce="300"
              v-model="tableFilter"
              placeholder="Поиск"
            >
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
          </template>

          <!-- Need buy -->
          <template #body-cell-need_buy="props">
            <q-td class="text-center" :props="props">
              <q-badge v-if="props.row.need_buy" color="green">Да</q-badge>
              <q-badge v-else color="orange">Нет</q-badge>
            </q-td>
          </template>

          <!-- Edible -->
          <template #body-cell-edible="props">
            <q-td class="text-center" :props="props">
              <q-badge v-if="props.row.edible" color="green">Да</q-badge>
              <q-badge v-else color="orange">Нет</q-badge>
            </q-td>
          </template>
        </q-table>
      </div>

      <transition
        appear
        enter-active-class="animated slideInRight"
        leave-active-class="animated slideOutRight"
      >
        <div
          class="col-12 col-md-3 col-lg-2 col-shrink"
          :class="$q.screen.gt.sm ? '' : 'order-first'"
          v-if="showFilters"
        >
          <q-card class="position-sticky">
            <q-card-section>
              <h6 class="q-my-sm text-center text-bold">Фильтры</h6>

              <q-form
                class="q-col-gutter-y-md"
                @submit="loadIngredients()"
                @reset="resetFilters()"
              >
                <div>
                  <span class="text-subtitle2"
                    >Найдено результатов:
                    {{ tablePagination.rowsNumber || "-" }}</span
                  >
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">
                    Категория заполнена
                  </h6>
                  <q-select
                    v-model="filters.hasCategory"
                    :options="optionsIsFilled"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">Категория</h6>
                  <q-select
                    v-model="filters.category"
                    :disable="filters.hasCategory !== null"
                    :options="ingredientCategories || []"
                    option-label="title"
                    option-value="id"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">Цена</h6>
                  <q-select
                    v-model="filters.hasPrice"
                    :options="optionsIsFilled"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">
                    Используется в рецептах
                  </h6>
                  <q-select
                    v-model="filters.hasRecipes"
                    :options="optionsIsTrueReversed"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">
                    Требует покупки
                  </h6>
                  <q-select
                    v-model="filters.needBuy"
                    :options="optionsIsTrue"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>
                <div>
                  <h6 class="q-my-sm text-subtitle2 text-bold">Съедобен</h6>
                  <q-select
                    v-model="filters.edible"
                    :options="optionsIsTrue"
                    class="q-px-md"
                    options-dense
                    dense
                    map-options
                    emit-value
                  />
                </div>

                <div class="row justify-around">
                  <q-btn type="reset" color="negative" size="sm" icon="close"
                    >Сбросить</q-btn
                  >
                  <q-btn type="submit" color="primary" size="sm" icon="search"
                    >Поиск</q-btn
                  >
                </div>
              </q-form>
            </q-card-section>
          </q-card>
        </div>
      </transition>
    </div>
  </q-page>
</template>

<script lang="ts">
import { useBaseStore } from "src/stores/base";
import { IngredientRead } from "src/client";
import { defineComponent } from "vue";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import { TablePagination, TablePropsOnRequest } from "src/modules/Globals";
import { debounce, QTableProps } from "quasar";
import { useAuthStore } from "src/stores/auth";
let tableColumns = [
  {
    name: "title",
    label: "Название",
    align: "left",
    field: "title",
    required: true,
    sortable: true,
  },
  {
    name: "category",
    label: "Категория",
    align: "left",
    required: true,
    sortable: true,
  },
  {
    name: "min_pack_size",
    label: "Размер упаковки",
    field: (row: IngredientRead) =>
      row.min_pack_size ? row.min_pack_size : "-",
    required: true,
    sortable: true,
  },
  {
    name: "price",
    label: "Цена",
    field: (row: IngredientRead) =>
      row.price ? String(row.price) + " ₺" : "-",
    required: true,
    sortable: true,
  },
  {
    name: "used_times",
    label: "В рецептах",
    field: "used_times",
    required: true,
    sortable: true,
    style: "width: 50px;",
  },
  {
    name: "need_buy",
    label: "Требует покупки",
    field: (row: IngredientRead) => (row.need_buy ? "Да" : "Нет"),
    align: "center",
    required: true,
    sortable: true,
    style: "width: 50px;",
  },
  {
    name: "edible",
    label: "Съедобен",
    field: (row: IngredientRead) => (row.edible ? "Да" : "Нет"),
    align: "center",
    required: true,
    sortable: true,
    style: "width: 50px;",
  },
] as QTableProps["columns"];

interface QueryInterface {
  [id: string]: string;
  // q?: string;
}

interface IngredientFilters {
  hasPrice?: boolean | null;
  hasRecipes?: boolean | null;
  hasCategory?: boolean | null;
  needBuy?: boolean | null;
  edible?: boolean | null;
  category?: boolean | null;
}

const filters = {
  hasPrice: null,
  hasRecipes: null,
  hasCategory: null,
  needBuy: null,
  edible: null,
  category: null,
} as IngredientFilters;

const filtersRemap = {
  hasPrice: "priceIsnull",
  hasRecipes: "recipesIsnull",
  needBuy: "needBuy",
  edible: "edible",
  hasCategory: "categoryIsnull",
  category: "category",
};

export default defineComponent({
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();

    // eslint-disable-next-line @typescript-eslint/no-empty-function
    const emptyFunc = () => {};

    if (tableColumns) {
      tableColumns[1].field = (row: IngredientRead) =>
        // eslint-disable-next-line @typescript-eslint/no-unsafe-return
        this.getCategoryById(row.category);
    }

    return {
      store,
      storeAuth,
      loading: false,
      // tableFilter: '',
      showFilters: this.$q.localStorage.getItem("ingredientsShowFilters"),
      optionsIsFilled: [
        { label: "-", value: null },
        { label: "Заполнено", value: false },
        { label: "Не заполнено", value: true },
      ],
      optionsIsTrue: [
        { label: "-", value: null },
        { label: "Да", value: true },
        { label: "Нет", value: false },
      ],
      optionsIsTrueReversed: [
        { label: "-", value: null },
        { label: "Да", value: false },
        { label: "Нет", value: true },
      ],
      tableColumns,
      tablePagination: {
        rowsPerPage: 20,
        page: 1,
        sortBy: "title",
        descending: false,
      } as TablePagination,
      filters: Object.assign({}, filters),
      filtersDefault: JSON.parse(JSON.stringify(filters)) as IngredientFilters,
      debounceLoadIngredients: emptyFunc,
    };
  },
  created() {
    // eslint-disable-next-line @typescript-eslint/unbound-method
    this.debounceLoadIngredients = debounce(this.loadIngredients, 1000);
    this.handleQueryChange(this.$query as QueryInterface);
    this.loadIngredients();
    if (!this.ingredientCategories) {
      this.loadIngredientCategories();
    }
  },
  methods: {
    loadIngredients(props?: TablePropsOnRequest) {
      let payload = {};
      this.loading = true;

      let pagination: TablePagination = Object.assign({}, this.tablePagination);
      if (props && props.pagination) {
        pagination = props.pagination;
      }

      Object.assign(payload, {
        search: this.tableFilter,
        ordering:
          (pagination.descending ? "-" : "") + String(pagination.sortBy),
        pageSize: pagination.rowsPerPage,
        page: pagination.page,
      });

      for (const [filterName, fieldName] of Object.entries(filtersRemap)) {
        // @ts-expect-error Custom filters
        let val = this.filters[filterName] as boolean | null;
        if (val !== null) {
          // @ts-expect-error Custom filters
          payload[fieldName] = val;
        }
        this.updateQueryParam(filterName, val);
      }

      this.store
        .loadIngredients(payload, true)
        .then((resp) => {
          this.loading = false;
          this.tablePagination = Object.assign({}, props?.pagination, {
            rowsNumber: resp.count,
          });
        })
        .catch((err: CustomAxiosError) => {
          this.handleErrors(err, "Ошибка загрузки ингредиентов");
        });
    },
    loadIngredientCategories() {
      let payload = {
        page_size: 1000,
      };
      // this.loading = true;

      this.store
        .loadIngredientCategories(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, "Ошибка загрузки категорий ингредиентов");
        });
    },
    updateQueryParam(field: string, value: unknown) {
      // console.debug('Set field: ', field, value);
      // @ts-expect-error Custom fields inserting
      (this.$query as QueryInterface)[field] = value;
      // console.debug('Q: ', this.$query);
    },
    handleQueryChange(query: QueryInterface) {
      for (const filterName of Object.keys(filtersRemap)) {
        let val: string | boolean | null = query[filterName];
        if (val === "false") {
          val = false;
        } else if (val === "true") {
          val = true;
        } else if (val === "null") {
          val = null;
        } else if (val === "") {
          val = null;
        }

        // console.debug('Unload field: ', query, filterName, val);
        // @ts-expect-error Custom filters
        this.filters[filterName] = val;
      }
    },
    getCategoryById(id: number | null): string | number | null {
      const cat = this.ingredientCategories?.find((i) => i.id == id);
      return cat?.title || id;
    },
    onRowClick(e: Event, row: IngredientRead) {
      void this.$router.push({ name: "ingredient", params: { id: row.id } });
    },
    resetFilters() {
      this.filters = Object.assign({}, this.filtersDefault);
      console.debug("Reset: ", this.filters);
    },
  },
  computed: {
    ingredients() {
      return this.store.ingredients;
    },
    ingredientCategories() {
      return this.store.ingredient_categories;
    },
    tableFilter: {
      get() {
        return (this.$query as QueryInterface).q || null;
      },
      set(val: string | null) {
        (this.$query as QueryInterface).q = val || "";
      },
    },
  },
  watch: {
    filters: {
      deep: true,
      handler() {
        this.tablePagination.page = 1;
        this.debounceLoadIngredients();
      },
    },
    showFilters(val) {
      this.$q.localStorage.set("ingredientsShowFilters", val);
    },
    $query: {
      deep: true,
      handler(val: QueryInterface) {
        this.handleQueryChange(val);
      },
    },
  },
});
</script>
