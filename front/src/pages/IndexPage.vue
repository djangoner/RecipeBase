<template>
  <q-page
    class="flex column"
    padding
  >
    <!-- Top metrics -->
    <div class="row q-col-gutter-md">
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

    <div>
      <index-page-status />
    </div>

    <!-- Center links -->
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
            <q-item-section>Список покупок</q-item-section>
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

    <!-- Bottom version -->
    <div class="flex flex-center">
      <span class="text-subtitle1 text-weight-bold">V {{ appVersion }}</span>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import IndexPageStatus from "../components/Status/IndexPageStatus.vue"
import MetricCard from "src/components/MetricCard.vue"
import { useBaseStore } from "src/stores/base"
import { computed, onMounted, ref } from "vue"
import { useAuthStore } from "src/stores/auth"
import { promiseSetLoading } from "src/modules/StoreCrud"
import { isOnline } from "src/modules/isOnline"
import {useIntervalFn} from '@vueuse/core'

const store = useBaseStore()
const storeAuth = useAuthStore()
const loading = ref(false)

const stats = computed(() => {
  return store.stats
})

const appVersion = computed(() => {
  return store.appVersion
})

function loadStats() {
  if (!isOnline.value){
    return
  }
  const prom = store
    .loadStats()
  promiseSetLoading(prom, loading)
}

onMounted(() => {
  loadStats()
})

useIntervalFn(() => {
  loadStats()
}, 15000)

</script>
