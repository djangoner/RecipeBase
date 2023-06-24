<template>
  <div class="row column q-gutter-y-md">
    <recipe-tags-select
      v-if="value.recommendations_tags"
      v-model="value.recommendations_tags"
      :readonly="!edit"
      label="Рекомендовать метки"
      outlined
    />
    <recipe-select
      v-model="value.recommendations_recipes"
      :readonly="!edit"
      label="Рекомендовать рецепты"
      multiple
      outlined
      use-chips
    />
  </div>
</template>

<script setup lang="ts">
import RecipeSelect from './RecipeSelect.vue'
import RecipeTagsSelect from './RecipeTagsSelect.vue'
import { RecipeRead } from "src/client"
import { computed, PropType } from "vue"

const props = defineProps({
  recipe: {
    type: Object as PropType<RecipeRead>,
    required: true,
  },
  edit: {
    type: Boolean,
    required: false,
  }
})

const $emit = defineEmits(["update:recipe"])

const value = computed({
  get() {
    return props.recipe
  },
  set(value) {
    $emit("update:recipe", value)
  },
})
</script>
