<template>
  <q-page class="q-pt-sm" padding>
    <!-- Compilations tabs -->
    <q-tabs
      v-model="compilation"
      content-class="text-grey-9"
      active-class="text-secondary"
    >
      <q-tab name="" icon="restaurant_menu" label="Все"></q-tab>
      <q-tab name="new" icon="hourglass_top" label="Новое"></q-tab>
      <q-tab name="top10" icon="grade" label="Топ 10"></q-tab>
      <q-tab name="long_uncooked" icon="history" label="4+ недели"></q-tab>
      <q-tab name="vlong_uncooked" icon="history" label="8+ недель"></q-tab>
      <q-tab name="archive" icon="archive" label="Архив"></q-tab>
    </q-tabs>

    <!-- Search input -->
    <q-input v-model="search" debounce="250" label="Поиск" autofocus clearable>
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
    ></q-select>

    <div class="row q-gutter-x-md items-center">
      <q-btn
        v-if="storeAuth.hasPerm('recipes.add_recipe')"
        class="q-my-sm"
        icon="add"
        color="secondary"
        size="sm"
        @click="openRecipe('new')"
        >Добавить рецепт</q-btn
      >
      <q-btn
        class="q-my-sm"
        icon="tune"
        color="primary"
        size="sm"
        @click="showFilters = !showFilters"
        >Фильтры</q-btn
      >

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
      ></q-btn-toggle>
    </div>

    <span v-if="recipes"> Найдено результатов: {{ tablePagination?.rowsNumber }} </span>

    <!-- Recipe cards -->
    <div
      class="row q-col-gutter-x-md q-col-gutter-y-md"
      :class="$q.screen.gt.sm ? 'no-wrap' : ''"
    >
      <div class="col q-mt-md" v-if="recipes">
        <!-- Cards mode -->
        <template v-if="displayMode == 'cards'">
          <!-- Pagination -->
          <div v-if="totalPages">
            <div class="flex justify-center q-mb-md">
              <q-pagination
                v-model="page"
                :max="totalPages"
                direction-links
              ></q-pagination>
            </div>
            <q-separator class="q-my-md" />
            <!-- /Pagination -->
          </div>
          <div class="recipes-row row q-col-gutter-x-md q-col-gutter-y-sm">
            <div
              class="col-xs-12 col-sm-6 col-md-4 col-lg-2"
              v-for="recipe of recipes"
              :key="recipe.id"
            >
              <!-- Recipe card -->
              <recipe-card :recipe="recipe" @updateItem="loadRecipes()"></recipe-card>
            </div>
          </div>

          <q-separator class="q-my-md" />

          <!-- Pagination -->
          <div
            class="flex justify-center q-mt-md"
            v-if="recipes.length > 0 && totalPages"
          >
            <q-pagination v-model="page" :max="totalPages" direction-links></q-pagination>
          </div>
          <!-- /Pagination -->
          <div class="flex justify-center items-center full-height" v-else>
            <h6 class="text-bold">Результатов не найдено</h6>
          </div>
        </template>
        <!-- Table mode -->
        <template v-else-if="displayMode == 'table'">
          <q-table
            title="Рецепты"
            :rows="recipes"
            :columns="tableColumns"
            :loading="loading"
            :filter="search"
            :rows-per-page-options="[1, 5, 10, 15, 20, 50]"
            @row-click="onRowClick"
            v-model:pagination="tablePagination"
            @request="loadRecipesTable"
            binary-state-sort
            :dense="$q.screen.lt.md"
          ></q-table>
        </template>
      </div>

      <transition
        appear
        enter-active-class="animated slideInRight"
        leave-active-class="animated slideOutRight"
      >
        <div
          class="col-12 col-md-3 col-lg-2 col-shrink"
          :class="$q.screen.gt.sm ? '' : 'order-first'"
          v-if="showFilters && recipes"
        >
          <q-card class="position-sticky">
            <q-card-section>
              <h6 class="q-my-sm text-center text-bold">Фильтры</h6>

              <q-form @submit="loadRecipes()" @reset="resetFilters()">
                <div class="q-my-sm">
                  <h6 class="q-my-sm text-subtitle2 text-bold">Время готовки</h6>
                  <q-range
                    v-model="filters.cooking_time"
                    class="q-px-md"
                    :min="5"
                    :max="120"
                    :step="5"
                    label
                  />
                </div>

                <div class="q-my-sm">
                  <h6 class="q-my-sm text-subtitle2 text-bold">Метки</h6>
                  <q-select
                    v-model="filters.tags_include"
                    label="Включить"
                    @filter="filterTagsInclude"
                    :options="tagList || []"
                    option-label="title"
                    option-value="id"
                    use-input
                    multiple
                    use-chips
                    map-options
                    emit-value
                    options-dense
                    dense
                  ></q-select>
                  <q-select
                    v-model="filters.tags_exclude"
                    label="Исключить"
                    @filter="filterTagsExclude"
                    :options="tagList || []"
                    option-label="title"
                    option-value="id"
                    use-input
                    multiple
                    use-chips
                    map-options
                    emit-value
                    options-dense
                    dense
                  ></q-select>
                </div>
                <div class="q-my-sm">
                  <h6 class="q-my-sm text-subtitle2 text-bold">Ингредиенты</h6>
                  <q-select
                    v-model="filters.ingredients_include"
                    label="Включить"
                    @filter="filterIngredientsInclude"
                    :options="ingredientList || []"
                    option-label="title"
                    option-value="id"
                    use-input
                    multiple
                    use-chips
                    map-options
                    emit-value
                    options-dense
                    dense
                  ></q-select>
                  <q-select
                    v-model="filters.ingredients_exclude"
                    label="Исключить"
                    @filter="filterIngredientsExclude"
                    :options="ingredientList || []"
                    option-label="title"
                    option-value="id"
                    use-input
                    multiple
                    use-chips
                    map-options
                    emit-value
                    options-dense
                    dense
                  ></q-select>
                </div>
                <div class="q-my-sm">
                  <h6 class="q-my-sm text-subtitle2 text-bold">Рейтинг</h6>
                </div>

                <div class="q-my-sm">
                  <div class="q-my-sm" v-for="user of usersRate" :key="user.id">
                    <div>
                      <div
                        class="row justify-between q-col-gutter-x-sm q-col-gutter-y-sm"
                      >
                        <span>
                          {{ userReadable(user) }}
                        </span>
                        <!-- <div class="row col-grow justify-between q-col-gutter-x-sm">
                          <div class="row items-center no-wrap">
                            <q-icon
                              v-if="rating.min === 0"
                              size="xs"
                              name="thumb_down"
                              color="grey"
                            >
                            </q-icon>
                            <template v-else>
                              <q-icon
                                v-for="i in Math.floor(rating.min)"
                                :key="i"
                                size="xs"
                                name="star_rate"
                                color="teal"
                              >
                              </q-icon>
                            </template>
                          </div>
                          <q-space />
                          <div
                            class="row items-center no-wrap"
                            :set="(rating = userRating(user))"
                          >
                            <q-icon
                              v-for="i in Math.floor(rating.max)"
                              :key="i"
                              size="xs"
                              name="star_rate"
                              color="teal"
                            >
                            </q-icon>
                          </div>
                        </div> -->
                      </div>
                    </div>

                    <q-range
                      :modelValue="userRating(user)"
                      @update:modelValue="userSetRating(user, $event)"
                      class="q-px-md"
                      :min="0"
                      :max="5"
                      label
                    >
                    </q-range>
                  </div>
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

      <q-inner-loading v-if="displayMode == 'cards'" :showing="loading"></q-inner-loading>
    </div>
  </q-page>
</template>

<script lang="ts">
import { useQuery } from '@oarepo/vue-query-synchronizer';
import recipeCard from 'components/RecipeCard.vue';
import { date, debounce, QTableProps } from 'quasar';
import {
  Ingredient,
  PaginatedRecipeReadList,
  RecipeRead,
  RecipeTag,
  User,
} from 'src/client';
import { TablePagination, TablePropsOnRequest } from 'src/modules/Globals';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { clearPayload } from 'src/modules/Utils';
import { useAuthStore } from 'src/stores/auth';
import { useBaseStore } from 'src/stores/base.js';
import { defineComponent } from 'vue';

const orderingOptions = [
  { label: 'Создан - по возрастанию', value: 'created' },
  { label: 'Создан - по убыванию', value: '-created' },
  { label: 'Последнее приготовление - по возрастанию', value: 'last_cooked' },
  { label: 'Последнее приготовление - по убыванию', value: '-last_cooked' },
];

let tableColumns = [
  {
    name: 'title',
    label: 'Название',
    align: 'left',
    field: 'title',
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
    name: 'cooking_time',
    label: 'Время',
    field: 'cooking_time',
    required: true,
    sortable: true,
    style: 'width: 40px',
  },
  {
    name: 'last_cooked',
    label: 'Приготовили',
    field: (r: RecipeRead) => date.formatDate(r.last_cooked, 'YYYY.MM.DD'),
    required: true,
    sortable: true,
    style: 'width: 40px',
  },
  {
    name: 'created',
    label: 'Создан',
    field: (r: RecipeRead) =>
      r.created ? date.formatDate(r.created, 'YYYY.MM.DD hh:mm') : '',
    required: true,
    sortable: true,
    style: 'width: 50px',
  },
] as QTableProps['columns'];

interface RangeValue {
  min: number;
  max: number;
}

interface RecipesFilters {
  cooking_time: {
    min: number;
    max: number;
  };
  tags_include: number[];
  tags_exclude: number[];
  ingredients_include: number[];
  ingredients_exclude: number[];
  ratings: {
    [key: number]: RangeValue;
  };
}

interface QueryInterface {
  compilation?: string;
  display: string;
}

export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { recipeCard },
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    let filters = {
      cooking_time: { min: 5, max: 120 },
      tags_include: [],
      tags_exclude: [],
      ingredients_include: [],
      ingredients_exclude: [],
      ratings: {},
    };

    // eslint-disable-next-line @typescript-eslint/no-empty-function
    const emptyFunc = () => {};

    return {
      store,
      $query: useQuery(),
      storeAuth,
      search: '',
      page: 1,
      page_size: 20,
      loading: false,
      tagList: null as RecipeTag[] | null,
      ingredientList: null as Ingredient[] | null,
      ordering: '-created',
      tablePagination: {
        rowsPerPage: 20,
        page: 1,
        sortBy: 'created',
        descending: true,
      } as TablePagination,
      // compilation: this.$query.compilation,
      showFilters: this.$q.localStorage.getItem('recipesShowFilters'),
      filters: Object.assign({}, filters) as RecipesFilters,
      filtersDefault: JSON.parse(JSON.stringify(filters)) as RecipesFilters,
      orderingOptions,
      debounceLoadRecipes: emptyFunc,
    };
  },
  created() {
    // eslint-disable-next-line @typescript-eslint/unbound-method
    this.debounceLoadRecipes = debounce(this.loadRecipes, 1000);
  },

  mounted() {
    void this.$nextTick(() => {
      void this.loadRecipes();
      if (!this.tags) {
        this.loadTags();
      }
      if (!this.users) {
        this.loadUsers();
      }
      if (!this.meal_time) {
        this.loadMealTime();
      }
      if (!this.ingredients) {
        this.loadIngredients();
      }
    });
  },

  methods: {
    loadRecipes() {
      return new Promise((resolve, reject) => {
        let payload = {} as { [key: string]: string };

        payload.search = this.search;
        payload.page = String(this.page);
        payload.page_size = String(this.page_size);

        if (this.compilation == 'top10') {
          payload.ordering = '';
          if (this.tablePagination.sortBy !== 'cooked_times') {
            this.tablePagination.sortBy = 'cooked_times';
            this.tablePagination.descending = true;
          }
        } else {
          payload.ordering = this.ordering;
          this.tablePagination.sortBy = this.ordering;
        }
        // Compilation
        if (this.compilation) {
          payload.compilation = this.compilation;
        }
        // Tags
        if (this.filters.tags_include) {
          payload.tagsInclude = this.filters.tags_include.join(',');
        }
        if (this.filters.tags_exclude) {
          payload.tagsExclude = this.filters.tags_exclude.join(',');
        }
        // Tags
        if (this.filters.ingredients_include) {
          payload.ingredientsInclude = this.filters.ingredients_include.join(',');
        }
        if (this.filters.ingredients_exclude) {
          payload.ingredientsExclude = this.filters.ingredients_exclude.join(',');
        }

        // Cooking time
        if (this.filters.cooking_time) {
          if (this.filters.cooking_time.min > 5) {
            payload.cookingTimeGt = String(this.filters.cooking_time.min);
          }
          if (this.filters.cooking_time.max < 120) {
            payload.cookingTimeLt = String(this.filters.cooking_time.max);
          }
        }

        // Ratings
        if (this.filters.ratings) {
          let r = [];
          for (const [user_id, values] of Object.entries(this.filters.ratings)) {
            if (values.min == values.max) {
              r.push(`${user_id}_${values.min}`);
              // payload.rating = `${user_id}_${values.min}`;
            } else {
              if (values.min > 0) {
                r.push(`${user_id}_+${values.min}`);
                // payload.rating = `${user_id}_+${values.min}`;
              }

              if (values.max < 5) {
                r.push(`${user_id}_-${values.max}`);
                // payload.rating = `${user_id}_-${values.max}`;
              }
            }
          }
          payload.rating = r.join(',');
        }

        // Send request

        this.loading = true;

        this.store
          .loadRecipes(clearPayload(payload))
          .then((resp: PaginatedRecipeReadList) => {
            this.loading = false;
            this.tablePagination.rowsNumber = resp?.count;
            resolve(resp);
          })
          .catch((err: CustomAxiosError) => {
            console.warn(err);
            reject(err);
            this.loading = false;
            this.handleErrors(err, 'Ошибка загрузки рецептов');
          });
      });
    },

    loadRecipesTable(props: TablePropsOnRequest) {
      console.debug('tableProps: ', props.pagination);
      this.ordering =
        props?.pagination?.descending && !props?.pagination?.sortBy?.startsWith('-')
          ? '-'
          : '';
      this.ordering += props?.pagination?.sortBy;
      this.page = props?.pagination?.page || 1;
      this.page_size = props?.pagination?.rowsPerPage || 20;
      void this.loadRecipes().then(() => {
        Object.assign(this.tablePagination, props.pagination);
      });
    },
    onRowClick(e: Event, row: RecipeRead) {
      this.openRecipe(row.id);
    },

    loadTags() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadTags(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки меток');
        });
    },
    loadIngredients() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadIngredients(payload)
        .then(() => {
          // this.ingredientList = resp.results;
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    loadMealTime() {
      let payload = {
        page_size: 1000,
      };
      // this.loading = true;

      this.store
        .loadMealTime(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки времени приема пищи');
        });
    },
    loadAmountTypes() {
      this.store
        .loadAmountTypes()
        .then(() => {
          // this.loading = false;
          // this.amountTypeList = this.amount_types?.types;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки типов измерений');
        });
    },
    loadUsers() {
      let payload = {
        page_size: 1000,
        can_rate: true,
      };
      this.storeAuth
        .loadUsers(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки пользователей');
        });
    },

    filterTagsInclude(val: string, update: CallableFunction) {
      update(() => {
        let isUsed = (tag: RecipeTag) => {
          return this.filters.tags_exclude.some((t) => t == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags;

        this.tagList =
          tags?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)) ||
          [];
        // console.debug(needle, this.tagList, tags);
      });
    },
    filterTagsExclude(val: string, update: CallableFunction) {
      update(() => {
        let isUsed = (tag: RecipeTag) => {
          return this.filters.tags_include.some((t) => t == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags;

        this.tagList =
          tags?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)) ||
          [];
        // console.debug(needle, this.tagList, tags);
      });
    },

    filterIngredientsInclude(val: string, update: CallableFunction) {
      update(() => {
        // let isUsed = (ingredient: Ingredient) => {
        //   return this.filters.ingredients_exclude.some((t) => t == ingredient.id);
        // };

        const needle = val.toLowerCase();
        let ingredients = this.ingredients;

        this.ingredientList = (
          ingredients?.filter(
            (v) => v.title.toLowerCase().indexOf(needle) > -1 // && !isUsed(v)
          ) || []
        ).slice(0, 20);
        // console.debug(needle, this.ingredientList, ingredients);
      });
    },
    filterIngredientsExclude(val: string, update: CallableFunction) {
      update(() => {
        // let isUsed = (ingredient: Ingredient) => {
        //   return this.filters.ingredients_include.some((t) => t == ingredient.id);
        // };

        const needle = val.toLowerCase();
        let ingredients = this.ingredients;

        this.ingredientList = (
          ingredients?.filter(
            (v) => v.title.toLowerCase().indexOf(needle) > -1 //  && !isUsed(v)
          ) || []
        ).slice(0, 20);
        // console.debug(needle, this.ingredientList, ingredients);
      });
    },
    userRating(user: User) {
      let exists = this.filters?.ratings[user.id];
      // console.debug('userRating: ', user, exists);

      if (exists) {
        return exists;
      } else {
        return { min: 0, max: 5 };
      }
    },
    userSetRating(user: User, rating: RangeValue) {
      // console.debug('setUserRating: ', user, rating);

      this.filters.ratings[user.id] = rating;
    },
    resetFilters() {
      this.filters = Object.assign({}, this.filtersDefault);
      this.filters.ratings = [];
      console.debug('Reset: ', this.filters);
    },

    openRecipe(id: number | 'new') {
      void this.$router.push({ name: 'recipe', params: { id: id } });
    },
    userReadable(user: User): string {
      if (user.first_name) {
        return user.first_name + ' ' + String(user.last_name);
      }
      return user.username;
    },
    shortText(tx: string, length = 100): string {
      if (tx.length < length) {
        return tx;
      } else {
        return tx.slice(0, length) + '...';
      }
    },
  },

  computed: {
    recipes() {
      return this.store.recipes;
    },
    users() {
      return this.storeAuth?.users;
    },
    usersRate() {
      let users = this.users;
      if (!users) {
        return users;
      }
      return users.filter((u) => {
        return u?.profile?.show_rate;
      });
    },
    tags() {
      return this.store.tags;
    },
    ingredients() {
      return this.store.ingredients;
    },
    amount_types() {
      return this.store.amount_types;
    },
    meal_time() {
      return this.store.meal_time;
    },
    compilation: {
      get() {
        return (this.$query as QueryInterface).compilation;
      },
      set(val: string) {
        (this.$query as QueryInterface).compilation = val;
      },
    },
    displayMode: {
      get() {
        return (this.$query as QueryInterface).display;
      },
      set(val: string) {
        (this.$query as QueryInterface).display = val;
      },
    },
    totalPages(): number | null {
      if (!this.tablePagination.rowsNumber || !this.tablePagination.rowsPerPage) {
        return null;
      }
      return (
        Math.ceil(this.tablePagination?.rowsNumber / this.tablePagination?.rowsPerPage) ||
        1
      );
    },
    tableColumns() {
      let r = tableColumns?.slice() || [];
      if (this.compilation == 'top10') {
        r.unshift({
          name: 'pos',
          label: '#',
          field: (r: RecipeRead) =>
            this.recipes
              ? String(this.recipes.indexOf(r) + 1 + (this.page - 1) * this.page_size)
              : '-',
          style: 'width: 20px',
          sortable: false,
          required: false,
        });
        r.splice(2, 0, {
          name: 'cooked_times',
          label: 'Кол-во',
          field: 'cooked_times',
          style: 'width: 20px',
          sortable: true,
          required: false,
        });
      } else if (this.compilation == 'new') {
        r = r.filter((c) => c.name !== 'last_cooked');
      }
      return r;
    },
  },

  watch: {
    search() {
      this.page = 1;
      void this.loadRecipes();
    },
    ordering() {
      void this.loadRecipes();
    },
    compilation() {
      this.page = 1;
      void this.loadRecipes();
    },
    page() {
      void this.loadRecipes();
    },
    filters: {
      deep: true,
      handler() {
        this.page = 1;
        this.debounceLoadRecipes();
      },
    },
    showFilters(val) {
      this.$q.localStorage.set('recipesShowFilters', val);
    },
  },
});
</script>

<style lang="scss" scoped>
.position-sticky {
  position: sticky;
  top: 60px;
}
</style>
