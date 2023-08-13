<template>
  <q-list
    class="q-my-sm"
    dense
  >
    <q-item
      v-for="ing of item.ingredients"
      :key="ing.id"
      class="items-center"
      clickable
      :to="{ name: 'recipe', params: { id: ing.recipe.id } }"
    >
      <q-item-section avatar>
        <small class="ing-day">{{ getRecipeDays(ing.recipe)?.join(",") }}.&nbsp;</small>
      </q-item-section>
      <q-item-section>
        {{ ing.recipe.title }} ({{ ingUsingStr(ing) }})
      </q-item-section>

      <recipe-card-tooltip
        v-if="ing.recipe"
        :recipe="ing.recipe"
      />
    </q-item>

    <template v-if="item.ingredient && item.ingredient.regular_ingredients">
      <q-separator />
      <q-item
        class="items-center q-mt-xs"
        items_center
        clickable
        :to="{
          name: 'recipe',
          params: { id: item.ingredient.regular_ingredients.id },
        }"
      >
        <q-item-section avatar>
          <small class="ing-day">-.&nbsp;</small>
        </q-item-section>
        <q-item-section>
          Регулярный ({{ item.ingredient.regular_ingredients.amount }} {{ item.ingredient.regular_ingredients.amount_type_str }})
        </q-item-section>
      </q-item>
    </template>

    <template v-if="item.ingredient && ingAccepted(item.ingredient)">
      <q-separator />
      <q-item class="items-center q-mt-xs">
        <q-item-section avatar>
          <small class="ing-day">-.&nbsp;</small>
        </q-item-section>
        <q-item-section>
          Рекомендация ({{ ingAccepted(item.ingredient).amount }} {{ ingAccepted(item.ingredient).amount_type_str }})
        </q-item-section>
      </q-item>
    </template>
  </q-list>
</template>

<script setup lang="ts">
import RecipeCardTooltip from '../RecipeCardTooltip.vue'
import { ProductListItemRead, RecipeIngredientWithRecipeRead, RecipeRead, RecipeShort } from "src/client"
import { WeekDaysShort } from "src/modules/WeekUtils"
import { useBaseStore } from "src/stores/base"
import { computed, PropType } from "vue"

interface ProductListItemAmount {
  amount: number
  amount_type: string
  amount_type_str: string
  amount_grams: number
  is_main: boolean
}

interface ProductListItemAmounts {
  [id: number]: ProductListItemAmount[]
}

const props = defineProps({
  item: {
    type: Object as PropType<ProductListItemRead>,
    required: true,
  },
})

const store = useBaseStore()

const plan = computed(() => {
  return store.week_plan
})

const recommendationAccepted = computed(() => plan.value?.recommendations_ingredients)

function ingAccepted(ing:RecipeIngredientWithRecipeRead ){
  return recommendationAccepted.value?.find(r => r.ingredient.id == ing.id)
}

function getRecipeDays(recipe: RecipeRead | RecipeShort): null | string[] {
  if (!plan.value) {
    return null
  }
  const plans = plan.value?.plans.filter((p) => p.recipe.id == recipe?.id)
  return plans?.map((p) => (p.day ? WeekDaysShort[p.day] : ("" as string))) || []
}

function ingUsingStr(ing: RecipeIngredientWithRecipeRead): string {
  const recipe = ing.recipe
  if (!recipe) {
    return ""
  }

  const amounts = props.item?.amounts as ProductListItemAmounts
  const ings = amounts[recipe.id] || []

  const texts = ings.map((i) => {
    let r = String(i.amount) + " " + i.amount_type_str
    if (i.is_main) {
      r += ", основной"
    }
    return r
  })
  return texts.join(", ")
}
</script>
