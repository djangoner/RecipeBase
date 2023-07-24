<template>
  <q-stepper
    v-if="stats"
    :model-value="step"
    flat
    :vertical="$q.screen.lt.md"
    inactive-color="grey"
    done-color="green"
    active-color="light-blue"
  >
    <q-step
      :done="step > 1"
      :name="1"
      title="План на неделю"
      icon="calendar_month"
      :caption="weekCaption"
    >
      <q-linear-progress
        :value="stats?.week_plan_progress"
      >
        <q-tooltip v-if="stats.week_plan_progress">
          {{ stats.week_plan_progress * 100 }}%
        </q-tooltip>
      </q-linear-progress>
    </q-step>
    <q-step
      :done="step > 2"
      :name="2"
      title="Список покупок"
      icon="list"
    />
    <q-step
      :done="step > 3"
      :name="3"
      title="Покупка продуктов"
      icon="shopping_cart"
    >
      <q-linear-progress
        :value="stats?.week_product_progress"
      >
        <q-tooltip v-if="stats.week_product_progress">
          {{ stats.week_product_progress * 100 }}%
        </q-tooltip>
      </q-linear-progress>
    </q-step>
  </q-stepper>
</template>

<script setup lang="ts">
import { useBaseStore } from "src/stores/base"
import { computed } from "vue"

const store = useBaseStore()

const stats = computed(() => {
  return store.stats
})

const step = computed(() => {
  if (!stats.value) {
    return 1
  }

  if (stats.value.week_product_progress >= 1){
    return 4
  }
  else if (stats.value.week_product_filled) {
    return 3
  } else if (stats.value.week_plan_progress >= 1 ||stats.value.week_plan_filled) {
    return 2
  }

  return 1
})

const weekCaption = computed(() => {
  if (!stats.value) {
    return ""
  }

  return `Неделя ${stats.value.year}-${stats.value.week}`
})
</script>
