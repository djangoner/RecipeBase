<template>
  <base-dialog
    v-model="model"
    title="Выбор рецепта"
  >
    <recipe-select
      placeholder="Выберите рецепт..."
      outlined
      @update:model-value="onSelect"
    />
  </base-dialog>
</template>

<script setup lang="ts">
import RecipeSelect from '../Recipes/RecipeSelect.vue'
import { useVModel } from '@vueuse/core';
import BaseDialog from '../common/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(["update:model-value", "select"])
const model = useVModel(props, 'modelValue', emit)

function onSelect(value: unknown){
  emit("select", value)
  model.value = false;
}

</script>