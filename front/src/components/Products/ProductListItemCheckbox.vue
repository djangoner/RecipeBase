<template>
  <q-checkbox
    :model-value="modelValue.is_completed"
    :color="modelValue.already_completed?'info':'primary'"
    checked-icon="task_alt"
    unchecked-icon="radio_button_unchecked"
    indeterminate-icon="help"
    size="lg"
    :disable="disable"
    @update:model-value="onUpdate"
  />
</template>

<script setup lang="ts">
import { ProductListItemRead } from 'src/client';
import { PropType } from 'vue';


const props = defineProps({
  modelValue: {
    type: Object as PropType<ProductListItemRead>,
    required: true,
  },
  disable: {
    type: Boolean,
    default: false,
  }
})

const $emit = defineEmits(["update:model-value"])


const onUpdate = (checkboxVal: boolean) => {
  const newItem = Object.assign({}, props.modelValue)
  newItem.is_completed = checkboxVal
  $emit('update:model-value', newItem)
}
</script>