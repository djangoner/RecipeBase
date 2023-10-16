<template>
  <select-recipe-dialog
    v-model="showSelectRecipe"
    @select="storeLocal.recipesSelectedAdd($event)"
  />
  <q-card
    flat
    bordered
  >
    <div class="text-subtitle1 text-center">
      Выбранные рецепты
      <small class="text-grey"> ({{ countNow }} / {{ countLimit }}) </small>
      <q-btn
        v-if="canAdd"
        icon="add"
        size="sm"
        color="positive"
        dense
        round
        unelevated
        @click="showSelectRecipe = true"
      />
    </div>
    <plan-drag-selected />
  </q-card>
</template>

<script setup lang="ts">
import SelectRecipeDialog from './SelectRecipeDialog.vue'
import { computed, ref } from 'vue';
import PlanDragSelected from './PlanDragSelected.vue'
import { useLocalStore } from 'src/stores/local';
import { storeToRefs } from 'pinia';
import { useBaseStore } from 'src/stores/base';
import { useShortcuts } from 'src/modules/VueUtils';

const store = useBaseStore()
const storeLocal = useLocalStore()
const { meal_time, week_plan } = storeToRefs(store)
const {recipesSelected} = storeToRefs(storeLocal)
const showSelectRecipe = ref(false)



const countNow = computed(() => recipesSelected.value.length)
const countLimit = computed(() => {
  if (!meal_time.value) {
    return 0
  }
  const fillDays = 7 // 5
  // const plansTotal = meal_time.value.filter((m) => m.is_primary).length * 5
  // const plansFilled = week_plan.value?.plans.filter((p) => p.meal_time.is_primary && p.day < 6).length
  const plansTotal = meal_time.value.filter((m) => m.is_primary).length * fillDays
  const plansFilled = week_plan.value?.plans.length || 0

  return plansTotal - plansFilled
})

const canAdd = computed(() => countNow.value < countLimit.value)


useShortcuts({
  "alt_a": () => showSelectRecipe.value = true,
})

</script>