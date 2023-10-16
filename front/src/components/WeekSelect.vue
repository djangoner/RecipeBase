<template>
  <q-bar class="bar_week_select col-grow">
    <div class="col text-bold">
      <div class="row justify-center items-center q-col-gutter-x-md">
        <q-btn
          icon="chevron_left"
          flat
          @click="changeWeek(-1)"
        />
        <span class="cursor-pointer q-px-md">{{ week_pick.year }}.{{ String(week_pick.week).padStart(2, "0") }} ({{ getDay(0) }} - {{ getDay(6) }})
          <q-menu>
            <q-date
              v-model="date_picker"
              first-day-of-week="1"
            />
          </q-menu>
        </span>
        <q-btn
          icon="chevron_right"
          flat
          @click="changeWeek(+1)"
        />
      </div>
    </div>
  </q-bar>
</template>

<script setup lang="ts">
import { date } from "quasar"
import { computed, nextTick, onMounted, PropType, ref, Ref, watch } from "vue"
import { DatePicker, YearWeek, YearWeekNullable, getDateOfISOWeek, getFirstDayOfWeek, getWeekNumber, getYearWeek } from "src/modules/WeekUtils"
import { useQuery } from "@oarepo/vue-query-synchronizer"
import { useShortcuts } from 'src/modules/VueUtils'

const props = defineProps({
  modelValue: { required: true, type: Object as PropType<YearWeek> },
  syncQuery: { type: Boolean, default: true },
})
const $emit = defineEmits(["update:model-value"])
const $query = useQuery()

const date_picker: Ref<DatePicker | string | null> = ref(null)
const week_pick: Ref<YearWeekNullable | Record<string, never>> = ref({})
const week_pick_old: Ref<YearWeekNullable | Record<string, never>> = ref({})

const modelValue = computed(() => props.modelValue)

function selectToday() {
  const [year, week] = getYearWeek()
  week_pick.value.year = year
  week_pick.value.week = week
  changeWeek(0)
}

function changeWeek(num: number): void {
  const min = 1
  const max = 53
  if (!week_pick.value.year || !week_pick.value.week) {
    return
  }

  week_pick.value.week += num

  if (week_pick.value.week < min) {
    week_pick.value.week = max
    week_pick.value.year -= 1
  } else if (week_pick.value.week > max) {
    week_pick.value.week = min
    week_pick.value.year += 1
  }
  updateDatePicker()
  // loadWeekPlan();
}

function updateDatePicker(): void {
  if (!week_pick.value.year || !week_pick.value.week) {
    return
  }
  // let d = new Date();
  const d = getDateOfISOWeek(week_pick.value.year, week_pick.value.week)
  const first = getFirstDayOfWeek(d)
  const last = first + 6
  // console.debug(first, last);
  const firstday = date.formatDate(new Date(d.setDate(first)).toDateString(), "YYYY/MM/DD")
  const lastday = date.formatDate(new Date(d.setDate(last)).toDateString(), "YYYY/MM/DD")
  date_picker.value = { from: firstday, to: lastday }
  console.debug("Datepicker upd: ", date_picker, week_pick.value.year)
}

function parseDatePicker(): void {
  if (typeof date_picker.value != "string") {
    return
  }
  console.debug("Parsing date: ", date_picker)
  const d = new Date(date_picker.value)
  console.debug(d, getWeekNumber(d))
  ;[week_pick.value.year, week_pick.value.week] = getWeekNumber(d)
  changeWeek(0)
}

function getDay(idx: number): string | undefined {
  if (!date_picker.value || typeof date_picker.value == "string") {
    return
  }
  const fday = new Date(date_picker.value.from)
  // let fday = getDateOfISOWeek(week_pick.year, week_pick.week);
  const day = fday.getDay()
  fday.setDate(fday.getDate() + day + idx - 1)
  return date.formatDate(fday, "DD.MM")
}

function isCurrentWeek(year: number, week: number){
  const [Cyear, Cweek] = getYearWeek()
  return (year == Cyear && week == Cweek)
}

function setFromQuery() {
  if (!($query.year && $query.week)) {
    return false
  }
  week_pick.value = { year: $query.year as number, week: $query.week as number }
  return true
}

onMounted(() => {
  if (!modelValue.value.year || !modelValue.value.week) {
    const fromQuery = setFromQuery()
    if (fromQuery) {
      updateDatePicker()
    } else {
      void nextTick(() => {
        selectToday()
      })
    }
  } else {
    week_pick.value = modelValue.value
    updateDatePicker()
  }
})

watch(date_picker, (val, oldVal) => {
  if (JSON.stringify(val) != JSON.stringify(oldVal)) {
    parseDatePicker()
  }
})
watch(modelValue, (val: YearWeek, oldVal: YearWeek) => {
  if (val !== oldVal) {
    week_pick.value = val
  }
})

watch(
  week_pick,
  (val: YearWeek) => {
    const notChanged = JSON.stringify(val) === JSON.stringify(week_pick_old)
    if (notChanged) {
      week_pick_old.value = Object.assign({}, val)
      return
    }
    console.debug("week_pick: ", notChanged, val, week_pick_old)
    week_pick_old.value = Object.assign({}, val)
    $emit("update:model-value", val)

    if (props.syncQuery) {
      if (isCurrentWeek(val.year, val.week)){
        $query.year = 0
        $query.week = 0
      } else {
        $query.year = val.year
        $query.week = val.week
      }
    }
  },
  { deep: true }
)

useShortcuts({
  "alt_[": () => changeWeek(-1),
  "alt_]": () => changeWeek(+1),
})

watch($query, () => {
  if ($query.year && $query.week && JSON.stringify({year: $query.year as number, week: $query.week as number}) != JSON.stringify(week_pick.value)){
    setFromQuery()
  }
})
</script>
