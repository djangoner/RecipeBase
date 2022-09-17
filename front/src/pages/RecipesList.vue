<template>
  <q-page padding>
    <!-- Compilations tabs -->
    <q-tabs v-model="this.filters.compilation">
      <q-tab :name="null" icon="restaurant_menu" label="Все"></q-tab>
      <q-tab name="long_uncooked" icon="history" label="Давно не готовили"></q-tab>
    </q-tabs>

    <!-- Search input -->
    <q-input v-model="search" debounce="250" label="Поиск" clearable>
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>

    <div class="row q-gutter-x-md">
      <q-btn
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
    </div>

    <span v-if="recipes"> Найдено результатов: {{ recipes.count }} </span>

    <!-- Recipe cards -->
    <div
      class="row q-col-gutter-x-md q-col-gutter-y-md"
      :class="$q.screen.gt.sm ? 'no-wrap' : ''"
    >
      <div class="col q-mt-md" v-if="recipes">
        <!-- Pagination -->
        <div>
          <div class="flex justify-center q-mb-md">
            <q-pagination
              v-model="page"
              :max="recipes.total_pages"
              direction-links
            ></q-pagination>
          </div>
          <q-separator class="q-my-md" />
          <!-- /Pagination -->
        </div>
        <div class="recipes-row row q-col-gutter-x-md q-col-gutter-y-sm">
          <div
            class="col-xs-12 col-sm-6 col-md-4 col-lg-3"
            v-for="recipe of recipes.results"
            :key="recipe.id"
          >
            <!-- Recipe card -->
            <recipe-card :recipe="recipe"></recipe-card>
          </div>
        </div>

        <q-separator class="q-my-md" />

        <!-- Pagination -->
        <div class="flex justify-center q-mt-md" v-if="recipes.results.length > 0">
          <q-pagination
            v-model="page"
            :max="recipes.total_pages"
            direction-links
          ></q-pagination>
        </div>
        <!-- /Pagination -->
        <div class="flex justify-center items-center full-height" v-else>
          <h6 class="text-bold">Результатов не найдено</h6>
        </div>
      </div>

      <transition
        appear
        enter-active-class="animated slideInRight"
        leave-active-class="animated slideOutRight"
      >
        <div
          class="col-12 col-md-3 col-shrink"
          :class="$q.screen.gt.sm ? '' : 'order-first'"
          v-if="showFilters && recipes"
        >
          <q-card>
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
                    :options="tagList"
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
                    :options="tagList"
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
                  <div
                    class="q-my-sm"
                    v-for="user of users"
                    :key="user.id"
                    :set="(rating = userRating(user))"
                  >
                    <div>
                      <div
                        class="row justify-between q-col-gutter-x-sm q-col-gutter-y-sm"
                      >
                        <span>
                          {{ userReadable(user) }}
                        </span>
                        <div class="row col-grow justify-between q-col-gutter-x-sm">
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
                        </div>
                      </div>
                    </div>

                    <q-range
                      :modelValue="rating"
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

      <q-inner-loading :showing="loading"></q-inner-loading>
    </div>
  </q-page>
</template>

<script>
import { useBaseStore } from 'stores/base.js';
import recipeCard from 'components/RecipeCard.vue';
import { debounce } from 'quasar';
import { useAuthStore } from 'src/stores/auth';

export default {
  components: { recipeCard },
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    let filters = {
      compilation: null,
      cooking_time: { min: 5, max: 120 },
      tags_include: [],
      tags_exclude: [],
      ratings: {},
    };

    return {
      store,
      storeAuth,
      search: '',
      page: 1,
      display_mode: 'cards',
      loading: false,
      tagList: null,
      showFilters: this.$q.localStorage.getItem('recipesShowFilters'),
      filters: Object.assign({}, filters),
      filtersDefault: filters,
    };
  },
  created() {
    this.debounceLoadRecipes = debounce(this.loadRecipes, 1000);
  },

  mounted() {
    this.loadRecipes();
    if (!this.tags) {
      this.loadTags();
    }
    if (!this.users) {
      this.loadUsers();
    }
  },

  methods: {
    loadRecipes() {
      let payload = new URLSearchParams();

      payload.append('search', this.search);
      payload.append('page', this.page);

      if (this.filters.compilation) {
        payload.append('compilation', this.filters.compilation);
      }

      if (this.filters.tags_include) {
        for (const tag of this.filters.tags_include) {
          payload.append('tags_include', tag);
        }
      }
      if (this.filters.cooking_time) {
        if (this.filters.cooking_time.min > 5) {
          payload.append('cooking_time_gt', this.filters.cooking_time.min);
        }
        if (this.filters.cooking_time.max < 120) {
          payload.append('cooking_time_lt', this.filters.cooking_time.max);
        }
      }
      if (this.filters.tags_exclude) {
        for (const tag of this.filters.tags_exclude) {
          payload.append('tags_exclude', tag);
        }
      }
      if (this.filters.ratings) {
        for (const [user_id, values] of Object.entries(this.filters.ratings)) {
          if (values.min == values.max) {
            payload.append('rating', `${user_id}_${values.min}`);
          } else {
            if (values.min > 0) {
              payload.append('rating', `${user_id}_+${values.min}`);
            }

            if (values.max < 5) {
              payload.append('rating', `${user_id}_-${values.max}`);
            }
          }
        }
      }

      this.loading = true;

      this.store
        .loadRecipes(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          console.warn(err);
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки рецептов');
        });
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
        .catch((err) => {
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
          this.ingList = this.ingredients?.results;
          // this.loading = false;
        })
        .catch((err) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    loadAmountTypes() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadAmountTypes(payload)
        .then(() => {
          // this.loading = false;
          this.amountTypeList = this.amount_types?.types;
        })
        .catch((err) => {
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
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки пользователей');
        });
    },

    filterTagsInclude(val, update, abort) {
      update(() => {
        let isUsed = (tag) => {
          return this.filters.tags_exclude.some((t) => t == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags?.results;

        this.tagList = tags?.filter(
          (v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)
        );
        // console.debug(needle, this.tagList, tags);
      });
    },
    filterTagsExclude(val, update, abort) {
      update(() => {
        let isUsed = (tag) => {
          return this.filters.tags_include.some((t) => t == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags?.results;

        this.tagList = tags?.filter(
          (v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)
        );
        // console.debug(needle, this.tagList, tags);
      });
    },
    userRating(user) {
      let exists = this.filters?.ratings[user.id];
      // console.debug('userRating: ', user, exists);

      if (exists) {
        return exists;
      } else {
        return { min: 0, max: 5 };
      }
    },
    userSetRating(user, rating) {
      // console.debug('setUserRating: ', user, rating);

      this.filters.ratings[user.id] = rating;
    },
    ressetFilters() {
      this.filters = Object.assign({}, filtersDefault);
    },

    openRecipe(id) {
      this.$router.push({ name: 'recipe', params: { id: id } }).catch((e) => {});
    },
    userReadable(user) {
      if (user.first_name) {
        return user.first_name + ' ' + user.last_name;
      }
      return user.username;
    },
    shortText(tx, length = 100) {
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
      return this.storeAuth?.users?.results;
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
  },

  watch: {
    search() {
      this.page = 1;
      this.loadRecipes();
    },
    page() {
      this.loadRecipes();
    },
    filters: {
      deep: true,
      handler(val, oldVal) {
        this.page = 1;
        this.debounceLoadRecipes();
      },
    },
    showFilters(val, oldVal) {
      this.$q.localStorage.set('recipesShowFilters', val);
    },
  },
};
</script>
