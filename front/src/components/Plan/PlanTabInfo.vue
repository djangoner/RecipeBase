<template>
  <div class="flex column">
    <div class="row q-mb-md">
      <q-badge>
        <span>Цена: </span> {{ pricePart }}₺ - <small>{{ priceFull }}₺</small>
      </q-badge>
    </div>

    <q-input
      type="textarea"
      class="col-grow"
      label="Заметки на неделю"
      outlined
      :input-style="{ resize: 'none' }"
      :debounce="0"
      :readonly="readonly"
      :model-value="currentComment"
      @update:model-value="updateComment"
      @blur="onBlur"
    />
  </div>
</template>

<script setup lang="ts">
import { sumArray } from "src/modules/Utils"
import { useBaseStore } from "src/stores/base"
import { computed, ref, watch } from "vue"

defineProps({
  readonly: {
    type: Boolean,
    default: false,
  }
})
const $emit = defineEmits(["update-plan"])

const store = useBaseStore()
const plan = computed(() => store.week_plan)
const changed = ref(false)

const commentId = "week"

const pricePart = computed(() => {
  return 0
  // return sumArray(plan.value?.plans.map((p) => p.recipe.price_part))
})

const priceFull = computed(() => {
  return 0
  // return sumArray(plan.value?.plans.map((p) => p.recipe.price_full))
})

const currentComment = computed(() => {
  return plan.value?.comments[commentId] as string | undefined || ""
})

const updateComment = (value: string | number) => {
  if (currentComment.value === undefined || plan.value?.comments === undefined){
    return
  }

  plan.value.comments[commentId] = value
  changed.value = true
  $emit("update-plan", false)
}

function onBlur(){ // Update plan on blur if changed
  if (changed.value){
    $emit('update-plan', true)
  }
}

watch(plan, () => {
  changed.value = false
})

</script>
