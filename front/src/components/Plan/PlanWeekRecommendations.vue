<!-- eslint-disable vue/no-v-for-template-key -->
<template>
  <q-expansion-item
    label="Рекомендации"
    dense
    dense-toggle
    default-opened
  >
    <q-card
      flat
      bordered
    >
      <q-card-section>
        <q-scroll-area style="height: 400px">
          <q-list
            v-if="recommendations && recommendations.length"
            dense
          >
            <template
              v-for="items, plan of recommendationsGrouped"
              :key="plan"
            >
              <q-expansion-item
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
                      <span class="text-grey">
                        {{ WeekDaysShort[getPlan(plan)?.day] }}.
                      </span>
                      {{ getPlan(plan)?.recipe?.title }}

                      <small class="text-grey">
                        ({{ getPlan(plan)?.meal_time?.title }})
                      </small>
                      <span class="text-grey">
                        {{ getItemsAccepted(items) }}/{{ getItemsAll(items) }}
                      </span>
                    </q-item-label>
                  </q-item-section>
                </template>

                <!-- Recipe Recommendations -->
                <plan-recommendation
                  v-for="(recommendation, idx) of items"
                  :key="idx"
                  :week="week"
                  :recommendation="recommendation"
                  @updated="onUpdated"
                />
              </q-expansion-item>
            </template>
          </q-list>
        </q-scroll-area>

        <q-inner-loading :showing="loading" />
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import PlanRecommendation from './PlanRecommendation.vue'
import { useDebounceFn } from "@vueuse/core"
import { YearWeek } from "src/modules/Globals"
import { promiseSetLoading } from "src/modules/StoreCrud"
import { useBaseStore } from "src/stores/base"
import { computed, onMounted, PropType, ref, watch } from "vue"
import { Recommendations } from 'src/client'
import { WeekDaysShort } from 'src/modules/WeekUtils'

const props = defineProps({
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  },
})

const $emit = defineEmits(["updated"])

const store = useBaseStore()
const loading = ref(false)

const debouncedLoad = useDebounceFn(loadRecommendations, 2000)

const recommendations = computed(() => store.weekRecommendations)

const recommendationsGrouped = computed(() => {
  if (!recommendations.value){
    return []
  }
  const res: Record<string, Recommendations[]> = {}

  for (const rec of recommendations.value) {
    if (!Object.hasOwn(res, rec.plan)){
      res[rec.plan] = []
    }
    res[rec.plan].push(rec)
  }

  return res
})

function loadRecommendations() {
  const prom = store.loadWeekRecommendations({ year: props.week.year, week: props.week.week })

  promiseSetLoading(prom, loading)
}

function onUpdated(){
  loadRecommendations()
  $emit("updated")
  console.debug("Updated recommendations, should reload plan")
}

function getPlan(id: number){
  return store.week_plan?.plans?.find(i => i.id == id)
}

function getItemsAccepted(items: Recommendations[]){
  return items.filter(i => i.accepted).length
}

function getItemsAll(items: Recommendations[]){
  return items.length
}

onMounted(() => {
  loadRecommendations()
  void store.loadIngredients({pageSize: 1000})
})

watch(
  () => store.week_plan,
  (val, oldVal) => {
    if (!oldVal){return}
    void debouncedLoad()
  },
  {deep: true}
)

watch(
  () => props.week,
  (val, oldVal) => {
    if (!oldVal){return}
    void debouncedLoad()
  }
)

defineExpose({onUpdated})
</script>
