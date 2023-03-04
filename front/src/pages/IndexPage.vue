<template>
  <q-page class="flex column q-gutter-y-lg">
    <div class="row q-px-md q-col-gutter-md">
      <metric-card
        @cardClick="$router.push({ name: 'recipes' })"
        icon="article"
        title="Рецептов"
        iconColor="light-blue-5"
        :value="stats?.recipes"
      ></metric-card>
      <metric-card
        @cardClick="$router.push({ name: 'ingredients' })"
        icon="shopping_basket"
        title="Ингредиентов"
        iconColor="cyan-5"
        :value="stats?.ingredients"
      ></metric-card>
      <metric-card
        @cardClick="$router.push({ name: 'week_plan' })"
        icon="calendar_month"
        title="Планов"
        iconColor="teal-5"
        :value="stats?.plans"
      ></metric-card>
      <metric-card
        @cardClick="$router.push({ name: 'tasks' })"
        icon="list"
        title="Задач"
        iconColor="green-5"
        :value="stats?.tasks"
      ></metric-card>
    </div>

    <div class="col-grow flex column flex-center q-col-gutter-y-lg">
      <div class="row justify-center items-center q-gutter-x-md">
        <q-icon name="restaurant" size="50px" color="primary" />
        <span class="text-bold text-h6"> База рецептов </span>
      </div>

      <div class="row">
        <q-list>
          <q-item :to="{ name: 'index' }"
            ><q-item-section avatar><q-icon name="home"></q-icon></q-item-section>
            <q-item-section>Главная</q-item-section>
          </q-item>
          <q-item
            :to="{ name: 'recipes' }"
            v-if="storeAuth.hasPerm('recipes.view_recipe')"
            ><q-item-section avatar><q-icon name="article"></q-icon></q-item-section>
            <q-item-section>Рецепты</q-item-section>
          </q-item>
          <q-item
            :to="{ name: 'week_plan' }"
            v-if="storeAuth.hasPerm('recipes.view_recipeplanweek')"
            ><q-item-section avatar
              ><q-icon name="calendar_month"></q-icon
            ></q-item-section>
            <q-item-section>План</q-item-section>
          </q-item>
          <q-item
            :to="{ name: 'product_list' }"
            v-if="storeAuth.hasPerm('recipes.view_productlistweek')"
            ><q-item-section avatar
              ><q-icon name="shopping_cart"></q-icon
            ></q-item-section>
            <q-item-section>Список продуктов</q-item-section>
          </q-item>
          <q-item
            :to="{ name: 'ingredients' }"
            v-if="storeAuth.hasPerm('recipes.view_ingredient')"
            ><q-item-section avatar
              ><q-icon name="shopping_basket"></q-icon
            ></q-item-section>
            <q-item-section>Ингредиенты</q-item-section>
          </q-item>
          <q-item :to="{ name: 'tasks' }" v-if="storeAuth.hasPerm('tasks.view_task')"
            ><q-item-section avatar><q-icon name="list"></q-icon></q-item-section>
            <q-item-section>Задачи</q-item-section>
          </q-item>
        </q-list>
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { StatsList } from 'src/client';
import MetricCard from 'src/components/MetricCard.vue';
import { useBaseStore } from 'src/stores/base';
import { Component, DefineComponent, defineComponent } from 'vue';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import IsOnlineMixin from 'src/modules/IsOnlineMixin';
import { useAuthStore } from 'src/stores/auth';
const card: DefineComponent = (MetricCard as Component) as DefineComponent;

export default defineComponent({
  components: { metricCard: card },
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  name: 'IndexPage',
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    return { store, storeAuth, loading: false };
  },
  mounted() {
    if (this.isOnLine) {
      this.loadStats();
    }
  },
  methods: {
    loadStats() {
      this.store
        .loadStats()
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки статистики');
        });
    },
  },
  computed: {
    stats(): StatsList | null {
      return this.store.stats;
    },
  },
});
</script>
