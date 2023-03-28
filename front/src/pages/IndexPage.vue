<template>
  <q-page class="flex column q-gutter-y-lg">
    <div class="row q-px-md q-col-gutter-md">
      <metric-card
        icon="article"
        title="Рецептов"
        icon-color="light-blue-5"
        :value="stats?.recipes"
        @card-click="$router.push({ name: 'recipes' })"
      />
      <metric-card
        icon="shopping_basket"
        title="Ингредиентов"
        icon-color="cyan-5"
        :value="stats?.ingredients"
        @card-click="$router.push({ name: 'ingredients' })"
      />
      <metric-card
        icon="calendar_month"
        title="Планов"
        icon-color="teal-5"
        :value="stats?.plans"
        @card-click="$router.push({ name: 'week_plan' })"
      />
      <metric-card
        icon="list"
        title="Задач"
        icon-color="green-5"
        :value="stats?.tasks"
        @card-click="$router.push({ name: 'tasks' })"
      />
    </div>

    <div class="col-grow flex column flex-center q-col-gutter-y-lg">
      <div class="row justify-center items-center q-gutter-x-md">
        <q-icon
          name="restaurant"
          size="50px"
          color="primary"
        />
        <span class="text-bold text-h6"> База рецептов </span>
      </div>

      <div class="row">
        <q-list>
          <q-item :to="{ name: 'index' }">
            <q-item-section avatar>
              <q-icon name="home" />
            </q-item-section>
            <q-item-section>Главная</q-item-section>
          </q-item>
          <q-item
            v-if="storeAuth.hasPerm('recipes.view_recipe')"
            :to="{ name: 'recipes' }"
          >
            <q-item-section avatar>
              <q-icon name="article" />
            </q-item-section>
            <q-item-section>Рецепты</q-item-section>
          </q-item>
          <q-item
            v-if="storeAuth.hasPerm('recipes.view_recipeplanweek')"
            :to="{ name: 'week_plan' }"
          >
            <q-item-section avatar>
              <q-icon name="calendar_month" />
            </q-item-section>
            <q-item-section>План</q-item-section>
          </q-item>
          <q-item
            v-if="storeAuth.hasPerm('recipes.view_productlistweek')"
            :to="{ name: 'product_list' }"
          >
            <q-item-section avatar>
              <q-icon name="shopping_cart" />
            </q-item-section>
            <q-item-section>Список продуктов</q-item-section>
          </q-item>
          <q-item
            v-if="storeAuth.hasPerm('recipes.view_ingredient')"
            :to="{ name: 'ingredients' }"
          >
            <q-item-section avatar>
              <q-icon name="shopping_basket" />
            </q-item-section>
            <q-item-section>Ингредиенты</q-item-section>
          </q-item>
          <q-item
            v-if="storeAuth.hasPerm('tasks.view_task')"
            :to="{ name: 'tasks' }"
          >
            <q-item-section avatar>
              <q-icon name="list" />
            </q-item-section>
            <q-item-section>Задачи</q-item-section>
          </q-item>
        </q-list>
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { StatsList } from "src/client";
import MetricCard from "src/components/MetricCard.vue";
import { useBaseStore } from "src/stores/base";
import { Component, DefineComponent, defineComponent } from "vue";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import IsOnlineMixin from "src/modules/IsOnlineMixin";
import { useAuthStore } from "src/stores/auth";
const card: DefineComponent = MetricCard as Component as DefineComponent;

export default defineComponent({
  name: "IndexPage",
  components: { metricCard: card },
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    return { store, storeAuth, loading: false };
  },
  computed: {
    stats(): StatsList | null {
      return this.store.stats;
    },
  },
  created() {
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
          this.handleErrors(err, "Ошибка загрузки статистики");
        });
    },
  },
});
</script>
