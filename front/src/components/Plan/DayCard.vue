<template>
  <q-card
    v-if="plan"
    class="row column justify-around q-px-xs q-py-sm full-height"
    :class="[
      dayIdx >= 6 ? 'bg-grey-3 print-hide print-week-hide' : '',
      WeekDaysColors[dayIdx],
      // isToday(getDay(dayIdx - 1)) ? 'shadow-5' : '',
      `weekday-${dayIdx}`,
    ]"
    style="min-height: 300px"
    flat
    bordered
  >
    <q-card-section class="row justify-between">
      <span
        class="text-h6"
        :class="isToday ? 'day-active' : ''"
      >
        <b>{{ dayStr }}</b> {{ WeekDays[dayIdx] }}
      </span>
      <button-comment
        v-model="plan.comments"
        :plan="plan"
        :day-idx="dayIdx"
        :day-str="dayStr"
        :can-edit="canEdit"
        @update-plan="$emit('update-plan')"
      />
    </q-card-section>

    <q-card-section>
      <div
        v-if="loading"
        class="q-gutter-y-md"
      >
        <q-skeleton type="QInput" />
        <q-skeleton type="QInput" />
      </div>
      <div
        v-else
        class="flex column"
      >
        <template v-for="mtime of meal_time">
          <div
            v-if="getDayPlans(dayIdx, mtime).length > 0 || mtime.is_primary"
            :key="mtime.id"
          >
            <div
              v-for="(dayPlan, rec_dayIdx) of getDayPlans(dayIdx, mtime)"
              :key="rec_dayIdx"
              class="row q-col-gutter-x-sm wrap"
            >
              <div class="col-auto">
                <div>
                  <span class="text-subtitle1 q-my-none relative-position q-py-xs">
                    {{ mtime.title }}
                    <q-badge
                      v-if="dayPlan && getWarning(dayPlan)"
                      :color="getWarningColor(dayPlan)"
                      rounded
                      floating
                    />
                  </span>
                  <q-icon
                    v-if="dayPlan?.recipe?.comment"
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
                      {{ dayPlan?.recipe?.comment }}
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
                  :model-value="dayPlan?.recipe"
                  :readonly="readonly"
                  @update:model-value="setRecipe(dayIdx, mtime, $event, rec_dayIdx)"
                />
                <!-- <span>{{ getplan(dayIdx, mtime)?.title }}</span> -->
              </div>

              <div
                v-if="dayPlan?.recipe"
                class="flex flex-center col-auto"
              >
                <q-btn
                  v-if="storeAuth.hasPerm('recipes.view_recipe')"
                  :to="{
                    name: 'recipe',
                    params: { id: dayPlan.recipe.id },
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
                  @click="delMealTime(mtime)"
                >
                  <q-tooltip>Убрать</q-tooltip>
                </q-btn>
              </div>

              <recipe-card-tooltip
                v-if="dayPlan?.recipe && $q.screen.gt.xs"
                :recipe="dayPlan.recipe"
              />
            </div>
          </div>
        </template>
      </div>
    </q-card-section>
    <q-space />

    <q-card-section>
      <div class="row q-mt-sm">
        <mealtime-select
          :readonly="props.readonly"
          :model-value="undefined"
          @update:model-value="addMtime"
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import RecipeCardTooltip from "../RecipeCardTooltip.vue"
import RecipeSelect from "../Recipes/RecipeSelect.vue"
import MealtimeSelect from "./MealtimeSelect.vue"
import ButtonComment from "./ButtonComment.vue"
import { useBaseStore } from "src/stores/base"
import { computed, PropType, ref } from "vue"
import { useAuthStore } from "src/stores/auth"
import { WarnedPlans, WeekDays } from "src/modules/Globals"
import { getWarningPriorityColor } from "src/modules/Utils"
import { MealTime, RecipePlan, RecipePlanRead, RecipeRead } from "src/client"

const props = defineProps({
  dayIdx: {
    type: Number,
    required: true,
  },
  dayStr: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  warnedPlans: {
    type: Object as PropType<WarnedPlans>,
    required: true,
  },
})
const $emit = defineEmits(["update-plan", "update-recipe"])

const store = useBaseStore()
const storeAuth = useAuthStore()

const saving = ref(false)

const plan = computed(() => {
  return store.week_plan
})

const canEdit = computed(() => {
  return storeAuth.hasPerm("recipes.change_recipeplanweek")
})

const isToday = computed(() => {
  const d = new Date()
  const d_str = String(d.getDate()) + "." + (d.getMonth() + 1).toString().padStart(2, "0")
  return props.dayStr == d_str
})

const meal_time = computed(() => {
  return store.meal_time
})

const WeekDaysColors: { [key: number]: string } = {
  1: "bg-amber-2",
  2: "bg-cyan-3",
  3: "bg-light-blue-3",
  4: "bg-blue-4",
  5: "bg-indigo-3",
}

function getWarning(plan: RecipePlanRead) {
  return props.warnedPlans[plan.id] || null
}
function getWarningColor(plan: RecipePlanRead) {
  const warn = getWarning(plan)
  return getWarningPriorityColor(warn.priority)
}

function getDayPlans(day: number, mtime: MealTime) {
  if (!plan.value) {
    return []
  }
  const plans = plan.value?.plans.filter((plan) => {
    return plan.day == day && plan.meal_time.id == mtime.id
  })

  if (mtime.is_primary) {
    if (plans.length < 1) {
      return [null]
    }
  }
  return plans //.map((r) => r.recipe);
}

function MealTimeFormat(raw: string | null) {
  if (!raw) {
    return raw
  }
  return raw.slice(0, raw.length - 3)
}

function addMtime(mtime: MealTime) {
  plan.value?.plans?.push(
    // @ts-expect-error: Meal time will be added
    Object.assign(
      {},
      {
        day: props.dayIdx,
        meal_time: mtime,
        recipe: null,
      }
    )
  )
}

function delMealTime(mtime: MealTime) {
  if (!plan.value) {
    return
  }
  const foundIdx = plan.value.plans.findIndex((p) => {
    // console.debug(p.day, props.dayIdx, p.meal_time.id, mtime.id, p.recipe)
    return p.day == props.dayIdx && p.meal_time == mtime && p.recipe == null
  })
  console.debug("delMealTime", mtime, foundIdx)
  if (foundIdx != -1) {
    plan.value.plans.splice(foundIdx, 1)
  }
}
function setRecipe(day: number, mtime: MealTime, value?: RecipeRead, rec_idx?: number) {
  console.debug("setRecipe: ", day, mtime, value)
  const plans =
    plan.value?.plans?.filter((plan) => {
      return plan.day == day && plan.meal_time.id == mtime.id
    }) || []

  const planItem = plans[rec_idx || 0]

  // const prom = plan?
  const newPlan: RecipePlan = Object.assign({}, planItem, {
    week: plan.value?.id,
    meal_time: mtime.id,
    day: day,
    recipe: value?.id,
  })
  let prom: Promise<RecipePlan>
  let action: "create" | "delete" | "update"

  if (planItem?.id && value) {
    prom = store.updateWeekPlanItem(planItem.id, newPlan)
    action = "update"
  } else if (planItem?.id) {
    prom = store.deleteWeekPlanItem(planItem.id)
    action = "delete"
  } else {
    prom = store.createWeekPlanItem(newPlan)
    action = "create"
  }

  saving.value = true
  void prom
    .then((resp: RecipePlan | undefined) => {
      $emit("update-recipe")
      const foundIdx = plan.value?.plans?.findIndex((p) => p.id === planItem?.id)

      if (resp && resp.id && plan.value) {
        console.debug("Updated/Created plan: ", resp.id, foundIdx, resp)

        if (foundIdx != -1) {
          plan.value.plans[foundIdx] = resp
        } else {
          plan.value.plans.push(resp)
        }
      } else if (action == "delete") {
        console.debug("Deleted plan: ", plan.value?.id, foundIdx)
        if (foundIdx != -1) {
          plan.value?.plans.splice(foundIdx, 1)
        }
      }
    })
    .finally(() => {
      saving.value = false
    })
}
</script>

<style lang="scss" scoped>
.day-active {
  text-decoration: underline;
}
</style>