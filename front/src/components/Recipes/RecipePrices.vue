<template>
  <q-expansion-item label="Цены">
    <q-markup-table flat>
      <thead>
        <tr>
          <th class="text-right">
            Название
          </th>
          <th class="text-right">
            Цена (необх.)
          </th>
          <th class="text-right">
            Цена (полная)
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="ing of recipe.ingredients"
          :key="ing.id"
        >
          <td class="text-right">
            {{ ing.ingredient?.title || "-" }}
          </td>
          <td class="text-right">
            {{ ing.price_part ? ing.price_part + "₺" : "-" }}
          </td>
          <td class="text-right">
            {{ ing.price_full ? ing.price_full + "₺" : "-" }}
          </td>
        </tr>
        <tr>
          <td class="text-right">
            <b>Итого</b>
          </td>
          <td class="text-right">
            {{ pricesPart || "0" }}₺
          </td>
          <td class="text-right">
            {{ pricesFull || "0" }}₺
          </td>
        </tr>
      </tbody>
    </q-markup-table>
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
  computed: {
    pricesPart(): number {
      return this.recipe?.ingredients?.map((i) => i.price_part).reduce((a, b) => a + b, 0) || 0
    },
    pricesFull(): number {
      return this.recipe?.ingredients?.map((i) => i.price_full).reduce((a, b) => a + b, 0) || 0
    },
  },
  methods: {
    dateFormat,
    dateTimeFormat,
  },
})
</script>
