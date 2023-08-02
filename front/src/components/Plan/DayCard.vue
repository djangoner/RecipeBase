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
        @update-plan="$emit('update-plan', true)"
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
            <draggable
              :list="getDayPlans(dayIdx, mtime)"
              :item-key="getItemKey"
              :sort="false"
              :data-day="dayIdx"
              :disabled="readonly || $q.screen.lt.md"
              group="plans"
              filter=".not-draggable"
              ghost-class="ghost-class"
              @move="onDrag"
              @change="onChange"
              @end="onEnd"
            >
              <!-- <div>{{ element }}</div> -->
              <template #item="{element, index}">
                <plan-item-row
                  :plan="element"
                  :index="index"
                  :mtime="mtime"
                  :warning="getWarning(element)"
                  :day-idx="dayIdx"
                  :readonly="readonly"
                  @delete-meal-time="delMealTime"
                  @set-recipe="setRecipe"
                />
              </template>
            </draggable>

            <!-- Recipe rows -->
            <!-- v-for="(dayPlan, rec_dayIdx) of getDayPlans(dayIdx, mtime)" -->
          </div>
        </template>
      </div>
    </q-card-section>
    <q-space />

    <!-- Bottom add mealtime -->

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
import PlanItemRow from './PlanItemRow.vue'

import MealtimeSelect from "./MealtimeSelect.vue"
import ButtonComment from "./ButtonComment.vue"
import { useBaseStore } from "src/stores/base"
import { computed, PropType, ref } from "vue"
import { useAuthStore } from "src/stores/auth"
import { WarnedPlans, WeekDays } from "src/modules/Globals"
import { MealTime, RecipePlan, RecipePlanRead, RecipeRead } from "src/client"
import draggable from 'vuedraggable'

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

function getWarning(plan: RecipePlanRead | null) {
  if (!plan){
    return null
  }
  return props.warnedPlans[plan.id] || null
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

function setRecipe(day: number, mtime: MealTime, value?: RecipeRead, rec_idx?: number, planItem?: RecipePlanRead) {
  console.debug("setRecipe: ", day, mtime, value)

  if (!planItem){
    const plans =
      plan.value?.plans?.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id
      }) || []
    planItem = plans[rec_idx || 0]
  }

  // const prom = plan?
  const newPlan: RecipePlan = Object.assign({}, planItem, {
    week: plan.value?.id,
    meal_time: mtime.id,
    day: day,
    recipe: value?.id,
  })
  let prom: Promise<RecipePlan>
  let action: "create" | "delete" | "update"
  const foundIdx = plan.value?.plans?.findIndex((p) => p.id === planItem?.id)

  if (foundIdx === -1 && !planItem?.id && !value?.id){
    console.debug("Empty set recipe prevented")
    return
  }

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

function getItemKey(item: RecipePlanRead | null){
  return item?.id || 0
}

function onDrag(e: Event, perform=false){
  // @ts-expect-error ignore
  // const elFrom = e.from as HTMLElement
  // @ts-expect-error ignore
  const elTo = e.to as HTMLElement
  // @ts-expect-error ignore
  const elItem = (e.dragged || e.item) as HTMLElement

  // const dayFrom = Number(elFrom.dataset.day) || null
  const dayTo = Number(elTo.dataset.day) || null
  const planId = Number(elItem.dataset.plan_id ) || null

  // console.debug("Drag", {dayFrom, dayTo, planId, perform}, e)
  if (!planId){
    // console.debug("Plan without ID ")
    return false
  }

  const planItem = plan.value?.plans.find(p => p.id == planId)
  if (!planItem){
    // console.debug("Plan not found ")
    return false
  }

  if (perform){
    if (dayTo && dayTo != planItem.day){
      setRecipe(dayTo, planItem.meal_time, planItem.recipe, 0, planItem)
    }
  }
}

function onEnd(e: Event){
  console.debug("END", e)
  onDrag(e, true)
}

function onChange(e, type){
  console.debug("Change", e, type)
}
</script>

<style lang="scss" scoped>
.day-active {
  text-decoration: underline;
}
</style>