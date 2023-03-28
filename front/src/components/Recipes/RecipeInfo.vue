<template>
  <q-expansion-item label="Подробности">
    <div
      v-if="recipe"
      class="row column q-px-md q-col-gutter-sm"
    >
      <span><b>Дата создания:</b> {{ dateTimeFormat(recipe.created) }}</span>
      <span><b>Дата изменения:</b> {{ dateTimeFormat(recipe.edited) }}</span>
      <span v-if="recipe.last_cooked"><b>Последний раз приготовлено:</b> {{ dateFormat(recipe.last_cooked) }}</span>
      <span v-if="recipe.cooked_times"><b>Приготовлено (раз):</b> {{ recipe.cooked_times }}</span>
      <span><b>Автор:</b> {{ recipe?.author?.username || "?" }}</span>
    </div>
  </q-expansion-item>
</template>

<script lang="ts">
import { RecipeRead } from "src/client"
import { defineComponent, PropType } from "vue"
import { dateFormat, dateTimeFormat } from "src/modules/Utils"

export default defineComponent({
  props: {
    recipe: {
      type: Object as PropType<RecipeRead>,
      required: true,
    },
  },
  methods: {
    dateFormat,
    dateTimeFormat,
  },
})
</script>
