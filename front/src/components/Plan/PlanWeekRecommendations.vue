<!-- eslint-disable vue/no-v-for-template-key -->
<template>
  <q-expansion-item
    class="col-grow flex column items-stretch recommendations-item"
    label="Рекомендации"
    dense
    dense-toggle
    default-opened
  >
    <q-card
      class="flex column items-stretch col-grow"
      flat
      bordered
    >
      <q-card-section>
        <div
          v-if="recommendations && recommendations.length && !planLoading"
          class="row"
        >
          <template
            v-for="[plan, items] of recommendationsGrouped"
            :key="plan"
          >
            <q-expansion-item
              class="col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3"
              default-opened
              dense
            >
              <!-- Recipe title -->
              <template #header>
                <q-item-section avatar>
                  <q-icon
                    name="calendar_month"
                    color="grey"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>
                    <span class="text-grey"> {{ WeekDaysShort[getPlan(plan)?.day] }}. <q-tooltip>{{ getPlan(plan) }}</q-tooltip></span>
                    {{ getPlan(plan)?.recipe?.title }}

                    <small class="text-grey"> ({{ getPlan(plan)?.meal_time?.title }}) </small>
                    <span class="text-grey"> {{ getItemsAccepted(items) }}/{{ getItemsAll(items) }} </span>
                  </q-item-label>
                </q-item-section>
              </template>

              <!-- Recipe Recommendations -->
              <plan-recommendation
                v-for="(recommendation, idx) of items"
                :key="idx"
                :week="week"
                :recommendation="recommendation"
                :edit="edit"
                @updated="onUpdated"
              />
            </q-expansion-item>
          </template>
        </div>

        <div
          v-else-if="planLoading"
          class="row"
        >
          <q-card
            v-for="i of 4"
            :key="i"
            class="col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3"
            flat
          >
            <q-card-section class="q-gutter-y-md">
              <q-skeleton
                v-for="i of 3"
                :key="i"
              />
            </q-card-section>
          </q-card>
        </div>

        <div
          v-else-if="!isLoading"
          class="flex flex-center"
        >
          <span class="text-h6 text-bold text-grey">Пока рекомендаций нет</span>
        </div>

        <q-inner-loading :showing="isLoading" />
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import PlanRecommendation from "./PlanRecommendation.vue"
import { useDebounceFn } from "@vueuse/core"
import { YearWeek } from "src/modules/Globals"
import { promiseSetLoading } from "src/modules/StoreCrud"
import { useBaseStore } from "src/stores/base"
import { computed, onMounted, PropType, ref, watch } from "vue"
import { Recommendations } from "src/client"
import { WeekDaysShort } from "src/modules/WeekUtils"

const props = defineProps({
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  },
  edit: {
    type: Boolean,
    default: false,
  },
  planLoading: {
    type: Boolean,
    default: false
  }
})

const $emit = defineEmits(["updated"])

const store = useBaseStore()
const isLoading = ref(false)

const debouncedLoad = useDebounceFn(loadRecommendations, 2000)

const recommendations = computed(() => store.weekRecommendations)


const recommendationsGrouped = computed(() => {
  if (!recommendations.value) {
    return []
  }
  const res: Record<string, Recommendations[]> = {}

  for (const rec of recommendations.value) {
    if (!Object.hasOwn(res, rec.plan)) {
      res[rec.plan] = []
    }
    res[rec.plan].push(rec)
  }
  const resArray = Object.entries(res)

  // Sort plans by day
  resArray.sort((a, b) => {
    const planA = getPlan(a[0])
    const planB = getPlan(b[0])

    if (planA?.day && planB?.day){
      return planA.day - planB.day
    }
    return 0
  })

  return resArray
})

function loadRecommendations() {
  if (!props.week?.year || !props.week?.week) {
    return
  }
  const prom = store.loadWeekRecommendations({ year: props.week.year, week: props.week.week })

  promiseSetLoading(prom, isLoading)
}

function onUpdated() {
  loadRecommendations()
  $emit("updated")
  console.debug("Updated recommendations, should reload plan")
}

function getPlan(id: number | string | null | undefined) {
  return store.week_plan?.plans?.find((i) => i.id == id)
}

function getItemsAccepted(items: Recommendations[]) {
  return items.filter((i) => i.accepted).length
}

function getItemsAll(items: Recommendations[]) {
  return items.length
}

onMounted(() => {
  loadRecommendations()
  void store.loadIngredients({ pageSize: 1000 })
})

watch(
  () => store.week_plan,
  (val, oldVal) => {
    if (!oldVal) {
      return
    }
    void debouncedLoad()
  },
  { deep: true }
)

watch(
  () => props.week,
  (val, oldVal) => {
    if (!oldVal?.week || !val?.week) {
      return
    }
    void debouncedLoad()
  }
)

defineExpose({ onUpdated })
</script>

<style lang="scss" scoped>
.recommendations-item {
  min-height: 300px;
  max-height: 550px;
  overflow-y: auto;

  :deep(.q-expansion-item__container) {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }
  :deep(.q-expansion-item__content) {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }
}
</style>
