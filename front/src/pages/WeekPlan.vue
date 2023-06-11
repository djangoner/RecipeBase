<template>
  <q-page
    id="week_plan_print"
    padding
    style="padding-top: 40px"
  >
    <div class="row items-center q-col-gutter-x-md print-hide">
      <div v-if="canEdit">
        <q-toggle
          v-model="editMode"
          label="Режим редактирования"
          :readonly="!canEdit"
        />
      </div>
      <q-space />
      <div v-if="plan && $q.screen.gt.sm">
        <small
          class="text-grey"
        >
          Время заполнения: {{ editedTimeStr }}
          <q-tooltip>
            Время заполнения плана
            ({{ dateTimeFormat(plan?.edited_first) }} - {{ dateTimeFormat(plan.edited_last) }})
          </q-tooltip>
        </small>
      </div>
      <div>
        <q-btn
          icon="menu"
          round
          dense
          flat
        >
          <q-menu>
            <q-list dense>
              <q-item
                clickable
                @click="onPrint()"
              >
                <q-item-section side>
                  <q-icon name="print" />
                </q-item-section>
                <q-item-section>
                  Распечатать план
                </q-item-section>
              </q-item>
              <q-item tag="label">
                <q-item-section side>
                  <q-toggle
                    v-model="enableFireworks"
                    dense
                  />
                </q-item-section>
                <q-item-section> Фейерверки </q-item-section>
              </q-item>
              <q-item
                clickable
                @click="showFireworks = true"
              >
                <!-- <q-item-section avatar /> -->
                <q-item-section> Запустить фейерверки </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <small
                    class="text-grey"
                  >
                    Время заполнения: {{ editedTimeStr }}
                    <q-tooltip>
                      Время заполнения плана
                      <br>
                      ({{ dateTimeFormat(plan?.edited_first) }} - {{ dateTimeFormat(plan.edited_last) }})
                    </q-tooltip>
                  </small>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </div>
    </div>

    <div class="week-select-page row wrap items-start q-col-gutter-x-sm q-col-gutter-y-md">
      <!-- :class="$q.screen.lt.md ? 'column' : ''" -->
      <template v-for="(day, idx) of WeekDays">
        <div
          v-if="idx > 0"
          :key="idx"
          class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3"
          :class="`weekday-col-${idx}`"
        >
          <day-card
            :day-idx="parseInt(idx)"
            :day-str="getDay(idx - 1)"
            :warned-plans="warnedPlans"
            :loading="loading"
            :readonly="readonly"
            @update-plan="saveWeekPlan"
            @update-recipe="onUpdateRecipe()"
          />
        </div>
      </template>

      <div
        v-if="plan"
        class="col weekplan_info"
      >
        <q-expansion-item
          label="Доп информация"
          dense
          dense-toggle
          default-opened
        >
          <q-card class="q-pt-none q-px-none">
            <q-card-section class="q-px-xs q-pt-none">
              <plan-week-info
                :plan="plan"
                :week="week"
              />
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </div>
    </div>

    <q-page-sticky
      position="top"
      expand
    >
      <week-select
        v-model="week"
        @update:model-value="loadWeekPlan()"
      />
      <q-linear-progress
        :value="fillingPrc || undefined"
        :indeterminate="saving"
        :instant-feedback="saving"
        :animation-speed="500"
      />
    </q-page-sticky>
  </q-page>

  <!-- Fireworks -->
  <Fireworks
    v-if="enableFireworks && showFireworks"
    ref="fw"
    :autostart="true"
    :options="fireworksOptions"
    :style="{
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      position: 'fixed',
      background: '#000',
      'z-index': 9999,
    }"
  />
  <!-- Fireworks overlay -->
  <div
    v-if="enableFireworks && showFireworks"
  >
    <div class="position-absolute absolute-top fireworks-overlay text-white">
      <div class="text-h6 text-center q-my-md">
        План заполнен за {{ editedTimeStr }}!
      </div>
    </div>
    <div
      class="position-absolute absolute-top-right fireworks-overlay"
    >
      <q-btn
        flat
        no-caps
        color="white"
        text-color="black"
        style="background: white"
        @click="showFireworks = false"
      >
        Закрыть
      </q-btn>
    </div>
  </div>

  <q-inner-loading :showing="loading" />
</template>

<script lang="ts" setup>
import DayCard from "../components/Plan/DayCard.vue"
import weekSelect from "components/WeekSelect.vue"
import { useBaseStore } from "src/stores/base"
import PlanWeekInfo from "src/components/PlanWeekInfo.vue"
import { computed, nextTick, onMounted, Ref, ref, watch } from "vue"
import { getDateOfISOWeek, YearWeek } from "src/modules/WeekUtils"
import { WeekDays } from "src/modules/WeekUtils"
import { useAuthStore } from "src/stores/auth"
// import VueHtmlToPaper from 'vue-html-to-paper';
// import { useQuery } from "@oarepo/vue-query-synchronizer";
import Fireworks from "@fireworks-js/vue"
import { useActiveElement, useDebounceFn, useStorage } from "@vueuse/core"
import { useQuery } from "@oarepo/vue-query-synchronizer"
import { isOnline } from "src/modules/isOnline"
import { RecipePlanWeekFromRead } from "src/Convert"
import { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { date, useQuasar } from "quasar"
import { WarningPriorities } from "src/modules/Globals"
import { useMagicKeys, whenever } from '@vueuse/core'
import { logicAnd } from '@vueuse/math'
import { dateTimeFormat } from "src/modules/Utils"

type QueryInterface = YearWeek

interface WarnedPlan {
  priority: string | null
  icon: string | null
}

interface WarnedPlans {
  [id: number]: WarnedPlan
}

const fireworksOptions = {
  opacity: 0.5,
  sound: {
    enabled: true,
    files: ["/sounds/explosion0.mp3", "/sounds/explosion1.mp3", "/sounds/explosion2.mp3"],
  },
}

const $query = useQuery()
const $q = useQuasar()
const store = useBaseStore()
const storeAuth = useAuthStore()

const editMode: Ref<boolean | null> = ref(null)
const loading = ref(false)
const saving = ref(false)
const enableFireworks = useStorage("enableFireworks", false)
const showFireworks = ref(false)

const week = computed({
  get() {
    return {
      year: ($query as QueryInterface)?.year as string | number | null,
      week: ($query as QueryInterface)?.week as string | number | null,
    } as YearWeek
  },
  set(val: YearWeek) {
    ;($query as QueryInterface).year = val?.year
    ;($query as QueryInterface).week = val?.week
  },
})

const canEdit = computed(() => {
  return storeAuth.hasPerm("recipes.change_recipeplanweek")
})

const readonly = computed(() => {
  return !editMode.value || !canEdit.value || !isOnline
})

const plan = computed(() => {
  return store.week_plan
})

const conditions = computed(() => {
  return store.conditions
})

const editedTimeStr = computed(() => {
  if (!plan.value){
    return "";
  }
  // const diff = Math.abs(new Date() - new Date(plan.value?.edited_first)) / 1000
  const diff = Math.abs(new Date(plan.value?.edited_last) - new Date(plan.value?.edited_first)) / 1000
  const hours = Math.floor(diff / 3600);
  const mins = Math.floor((diff / 60) % 60)
  const secs = Math.floor((diff) % 60)
  let res = '';
  const pad = (num: number) => {
    return num.toString().padStart(2, '0')
  }

  if (hours){
    res += `${pad(hours)}:`
  }
  if (mins){
    res += `${pad(mins)}:`
  }
  if (secs){
    res += `${pad(secs)}`
  }
  return res;
})

function onUpdateRecipe(){
  if (plan.value){
    if (!plan.value?.edited_first){
      plan.value.edited_first = new Date().toISOString()
    }
    plan.value.edited_last = new Date().toISOString()
  }
  void debouncedLoadWarnings()
}

const debouncedLoadWarnings = useDebounceFn(() => {
  if (!week.value || !week.value.year){
    console.debug("re-running debounced load warnings")
    void debouncedLoadWarnings()
  }
  void store.loadWeekWarnings({year: week.value.year, week: week.value.week})
}, 2000)

// const fw = ref(null)
// const refFireworks = computed(() => {
//   return fw.value
// })
const warnedPlans = computed(() => {
  const warnings = store.condWarnings || []
  const res: WarnedPlans = {}

  for (const warning of warnings) {
    let cond = getCondition(warning.condition)
    const plan = warning.plan
    if (!Object.hasOwn(res, plan)) {
      cond = getCondition(warning.condition)
      res[plan] = {
        icon: String(cond?.icon) || null,
        priority: String(cond?.priority) || null,
      }
    }

    const prioritySaved = WarningPriorities.indexOf(res[plan].priority || "")
    const priorityCurr = WarningPriorities.indexOf(String(cond?.priority) || "")

    if (priorityCurr > prioritySaved) {
      res[plan].priority = WarningPriorities[priorityCurr]
    }
  }
  return res
  // return [...new Set(plans)];
})

const meal_time = computed(() => {
  return store.meal_time
})
const fillingPrc = computed(() => {
      if (!meal_time.value) {
        return null
      }
      const plans = store.week_plan?.plans
      let plansFilled
      if (plans) {
        plansFilled = plans.filter((p) => p.meal_time.is_primary && p.day < 6).length
      }
      const plansTotal = meal_time.value.filter((m) => m.is_primary).length * 5

      if (!plansFilled || !plansTotal) {
        return 0
      }

      return plansFilled / plansTotal
})

function onPrint() {
  console.debug("Print before")
  store.printMode = true
  void nextTick(() => {
    window.print()
    store.printMode = false
    console.debug("Print after")
  })
}

function loadWeekPlan() {
  if (!week.value?.year || !week.value?.week) {
    return
  }
  const payload = {
    year: week.value.year,
    week: week.value.week,
  }
  loading.value = true

  store
    .loadWeekPlan(payload)
    .then(() => {
      loading.value = false
      if (editMode.value === null) {
        editMode.value = !(plan.value?.plans && plan.value?.plans?.length > 0)
      }
    })
    .catch(() => {
      loading.value = false
    })
}
function saveWeekPlan() {
  // let payload = Object.assign({}, plan);
  const payload = RecipePlanWeekFromRead(Object.assign({}, plan.value))
  delete payload["plans"]
  saving.value = true
  console.debug("Save: ", payload)

  store
    .saveWeekPlan(payload)
    .then(() => {
      saving.value = false
    })
    .catch(() => {
      saving.value = false
    })
}
function markPlanCompleted() {
  if (!plan.value) {
    return
  }
  plan.value.is_filled = true
  saveWeekPlan()
  showFireworks.value = true
}
function getDay(idx: number): string {
  const fday = getDateOfISOWeek(week.value.year, week.value.week)
  fday.setDate(fday.getDate() + idx)
  return date.formatDate(fday, "DD.MM")
}
function getCondition(id: number) {
  return conditions.value?.find((c) => c.id == id) || null
}
function askPlanCompleted(){
      $q.dialog({
        title: "Подтверждение",
        message: `Отметить план как завершенный?`,
        cancel: true,
        persistent: true,
      })
      .onOk(() => {
        markPlanCompleted()
      })
    }

    function loadMealTime(){
      void store.loadMealTime({pageSize: 1000})
    }

onMounted(() => {
  loadMealTime()
})

watch(fillingPrc, (val, oldVal) => {
      // When plan finished, show fireworks if enabled
      if (val == 1 && oldVal && !plan.value?.is_filled) {
        askPlanCompleted()
        // this.showFireworks = true
      }
    })

// Shortcuts
const activeElement = useActiveElement()

const notUsingInput = computed(() =>
  activeElement.value?.tagName !== 'INPUT'
  && activeElement.value?.tagName !== 'TEXTAREA',
)

const keys = useMagicKeys()

whenever(logicAnd(keys.shift_e, notUsingInput, canEdit), () => {
  console.debug("Toggle edit!",)
  editMode.value = !editMode.value
})

</script>

<style lang="scss">
body.body--dark .week-select-page {
  .q-card {
    color: black !important;
  }
}
body.body--dark .week-select-page .q-field--dark {
  .q-field__label,
  .q-field__input,
  .q-field__marginal {
    color: black;
  }
  .q-field__control:before {
    border-color: black;
  }
}

.fireworks-overlay {
  z-index: 99999;
}
</style>
