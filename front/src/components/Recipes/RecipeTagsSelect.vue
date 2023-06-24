<template>
  <q-select
    v-model="value"
    :label="label"
    :options="tags"
    option-label="title"
    options-dense
    dense
    multiple
    use-chips
    map-options
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { RecipeTag } from 'src/client';
import { useBaseStore } from 'src/stores/base';
import { computed, PropType } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array as PropType<RecipeTag[]>,
    required: true,
  },
  label: {
    type: String,
    default: "Метки рецепта"
  }
})
const $emit = defineEmits(["update:model-value"])
const store = useBaseStore()

const value = computed({
  get(){
    return props.modelValue
  },
  set(value){
    $emit("update:model-value", value)
  }
})

const tags = computed(() => store.tags)


</script>