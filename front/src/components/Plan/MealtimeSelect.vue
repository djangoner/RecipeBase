<template>
  <q-select
    v-model="model"
    class="col"
    :options="MealtimeOptions || []"
    :input-debounce="0"
    :readonly="readonly"
    option-value="id"
    option-label="title"
    label="Добавить"
    map-options
    use-input
    options-dense
    dense
    @filter="filterMealTime"
  />
</template>

<script setup lang="ts">
import { MealTime } from 'src/client';
import { useBaseStore } from 'src/stores/base';
import { computed, PropType, Ref, ref } from 'vue';


const props = defineProps({
  modelValue: {
    type: Object as PropType<MealTime>,
    default: null,
    required: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  }
})

const $emit = defineEmits(["update:model-value"])

const store = useBaseStore()
const MealtimeOptions: Ref<MealTime[]> = ref([])

const model = computed({
  get(){
    return props.modelValue
  },
  set(val: MealTime){
    console.debug("Meal time select: ", val)
    $emit("update:model-value", val)
  }
})

const mealTime = computed(() => {
  return store.meal_time
})

function filterMealTime(val: string, update: CallableFunction) {
      update(() => {
        // let isUsed = (mtime: MealTime) => {
        //   //   // console.debug(ing, this.recipe.ingredients);
        //   return this.plan?.plans.some((plan) => {
        //     return plan.meal_time.id == mtime.id;
        //   });
        //   //   return this.recipe.ingredients.some((t) => t.ingredient.id == ing.id);
        // };
        const needle = val.toLowerCase()

        MealtimeOptions.value = mealTime.value?.filter((v) => !v.is_primary && v.title.toLowerCase().indexOf(needle) > -1) || []
      })
    }

</script>