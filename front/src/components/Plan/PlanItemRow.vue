<template>
  <div
    :key="index"
    class="row q-col-gutter-x-sm wrap"
    :class="[plan?.recipe ? '' : 'not-draggable']"
    :data-plan_id="plan?.id"
  >
    <div class="col-auto">
      <div>
        <span class="text-subtitle1 q-my-none relative-position q-py-xs">
          {{ mtime.title }}
          <q-badge
            v-if="plan && warning"
            :color="warningColor"
            rounded
            floating
          />
        </span>
        <q-icon
          v-if="plan?.recipe?.comment"
          name="notes"
          size="xs"
          color="primary"
        >
          <q-tooltip
            anchor="top middle"
            self="bottom middle"
            :offset="[10, 10]"
          >
            Комментарий:
            {{ plan?.recipe?.comment }}
          </q-tooltip>
        </q-icon>
        <q-tooltip>
          {{ mtime.title }} -
          {{ MealTimeFormat(mtime.time || null) }}
        </q-tooltip>
      </div>
    </div>

    <div class="col">
      <recipe-select
        :key="index"
        :model-value="plan?.recipe"
        :readonly="readonly"
        :index="index"
        @update:model-value="$emit('set-recipe', dayIdx, mtime, $event, index)"
      />
      <!-- <span>{{ getplan(dayIdx, mtime)?.title }}</span> -->
    </div>

    <div
      v-if="plan?.recipe"
      class="flex flex-center col-auto"
    >
      <q-btn
        v-if="storeAuth.hasPerm('recipes.view_recipe')"
        :to="{
          name: 'recipe',
          params: { id: plan.recipe.id },
        }"
        icon="open_in_new"
        size="sm"
        flat
        dense
        round
      >
        <q-tooltip>Открыть рецепт</q-tooltip>
      </q-btn>
    </div>
    <div
      v-else-if="!mtime.is_primary"
      class="flex flex-center col-auto"
    >
      <q-btn
        icon="close"
        size="sm"
        flat
        dense
        round
        @click="$emit('delete-meal-time', mtime)"
      >
        <q-tooltip>Убрать</q-tooltip>
      </q-btn>
    </div>

    <recipe-card-tooltip
      v-if="plan?.recipe && $q.screen.gt.xs"
      :recipe="plan.recipe"
    />
  </div>
</template>
<script setup lang="ts">
import { getWarningPriorityColor } from "src/modules/Utils"
import RecipeCardTooltip from "../RecipeCardTooltip.vue"
import RecipeSelect from "../Recipes/RecipeSelect.vue"
import { WarnedPlan } from "src/modules/Globals"
import { computed, PropType } from "vue"
import { MealTime, RecipePlanRead } from "src/client"
import { useAuthStore } from "src/stores/auth"

const props = defineProps({
  plan: {
    type: Object as PropType<RecipePlanRead | null>,
    required: false,
    default: null,
  },
  index: {
    type: Number,
    required: true,
  },
  dayIdx: {
    type: Number,
    required: true,
  },
  mtime: {
    type: Object as PropType<MealTime>,
    required: true,
  },
  warning: {
    type: Object as PropType<WarnedPlan | null>,
    required: false,
    default: null,
  },
  readonly: {
    type: Boolean,
    required: true,
  },
})
const $emit = defineEmits(["delete-meal-time", "set-recipe"])

const storeAuth = useAuthStore()

const warningColor = computed(() => {
  const warn: WarnedPlan | null | undefined = props.warning
  if (!warn) {
    return ""
  }
  return getWarningPriorityColor(warn.priority)
})

function MealTimeFormat(raw: string | null) {
  if (!raw) {
    return raw
  }
  return raw.slice(0, raw.length - 3)
}
</script>
