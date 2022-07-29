<template>
  <q-page padding>
    <!-- Search input -->
    <q-input v-model="search" debounce="250" label="Поиск" clearable>
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>

    <q-btn
      class="q-my-sm"
      icon="add"
      color="secondary"
      size="sm"
      @click="openRecipe('new')"
      >Добавить рецепт</q-btn
    >

    <!-- Recipe cards -->
    <div class="q-mt-md" v-if="recipes">
      <!-- Pagination -->
      <div>
        <div class="flex justify-center q-mb-md" v-if="recipes.results.length > 10">
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
          <q-card
            class="cursor-pointer q-hoverable"
            v-ripple
            @click="openRecipe(recipe.id)"
          >
            <span class="q-focus-helper"></span>
            <q-card-section>
              <div class="flex justify-center items-center" style="min-height: 100px">
                <!-- <q-icon name="restaurant_menu" size="50px" color="grey"></q-icon> -->
                <q-img
                  :src="recipe.images ? recipe.images[0]?.image : null"
                  width="100%"
                  height="200px"
                  fit="cover"
                  style="max-height: 200px"
                >
                  <div class="absolute-bottom text-subtitle1 text-center">
                    {{ recipe.title }}
                  </div>
                </q-img>
              </div>
            </q-card-section>

            <q-card-section>
              <span class="text-subtitle2">{{ recipe.short_description }}</span>
            </q-card-section>
          </q-card>
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

    <q-inner-loading :showing="loading"></q-inner-loading>
  </q-page>
</template>

<script>
import { useBaseStore } from 'stores/base.js';

export default {
  data() {
    const store = useBaseStore();

    return {
      store,
      search: '',
      page: 1,
      display_mode: 'cards',
      loading: false,
    };
  },

  mounted() {
    this.loadRecipes();
  },

  methods: {
    loadRecipes() {
      let payload = {
        search: this.search,
        page: this.page,
        // page_size: 1,
      };
      this.loading = true;

      this.store
        .loadRecipes(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          console.warn(err);
          this.loading = false;
          this.handleError(err, 'Ошибка загрузки рецептов');
        });
    },

    openRecipe(id) {
      this.$router.push({ name: 'recipe', params: { id: id } }).catch((e) => {});
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
  },

  watch: {
    search() {
      this.loadRecipes();
    },
    page() {
      this.loadRecipes();
    },
  },
};
</script>
