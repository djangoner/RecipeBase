<template>
  <q-bar class="bar_week_select col-grow">
    <div class="col text-bold">
      <div class="row justify-center items-center q-col-gutter-x-md">
        <q-btn
          icon="chevron_left"
          flat
          @click="changeWeek(-1)"
        />
        <span class="cursor-pointer q-px-md">{{ week_pick.year }}.{{
          String(week_pick.week).padStart(2, "0")
        }}
          ({{ getDay(0) }} - {{ getDay(6) }})
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

<script lang="ts">
import { useBaseStore } from "src/stores/base";
import { date } from "quasar";
import { defineComponent, PropType } from "vue";
import {
  DatePicker,
  YearWeek,
  YearWeekNullable,
  WeekDays,
  getDateOfISOWeek,
  getFirstDayOfWeek,
  getWeekNumber,
  getYearWeek,
} from "src/modules/WeekUtils";

export default defineComponent({
  props: {
    modelValue: { required: true, type: Object as PropType<YearWeek> },
  },
  emits: ['update:model-value'],
  data() {
    const store = useBaseStore();
    return {
      store,
      date_picker: null as DatePicker | string | null,
      week_pick: {} as YearWeekNullable,
      week_pick_old: {},
      WeekDays,
    };
  },
  watch: {
    date_picker(val, oldVal) {
      if (JSON.stringify(val) != JSON.stringify(oldVal)) {
        this.parseDatePicker();
      }
    },
    modelValue(val: YearWeek, oldVal: YearWeek) {
      console.debug("modelValue: ", val, oldVal);
      if (val !== oldVal) {
        this.week_pick = val;
      }
    },
    week_pick: {
      deep: true,
      handler: function (val: YearWeek) {
        const notChanged =
          JSON.stringify(val) === JSON.stringify(this.week_pick_old);
        if (notChanged) {
          this.week_pick_old = Object.assign({}, val);
          return;
        }
        console.debug("week_pick: ", notChanged, val, this.week_pick_old);
        this.week_pick_old = Object.assign({}, val);
        this.$emit("update:model-value", val);
      },
    },
  },
  created() {
    if (!this.modelValue.year || !this.modelValue.week) {
      this.selectToday();
    } else {
      this.week_pick = this.modelValue;
      this.updateDatePicker();
    }
  },
  methods: {
    selectToday() {
      const [year, week] = getYearWeek();
      this.week_pick.year = year;
      this.week_pick.week = week;
      this.changeWeek(0);
    },
    changeWeek(num: number): void {
      const min = 1;
      const max = 53;
      if (!this.week_pick.year || !this.week_pick.week) {
        return;
      }

      this.week_pick.week += num;

      if (this.week_pick.week < min) {
        this.week_pick.week = max;
        this.week_pick.year -= 1;
      } else if (this.week_pick.week > max) {
        this.week_pick.week = min;
        this.week_pick.year += 1;
      }
      this.updateDatePicker();
      // this.loadWeekPlan();
    },
    updateDatePicker(): void {
      if (!this.week_pick.year || !this.week_pick.week) {
        return;
      }
      // let d = new Date();
      const d = getDateOfISOWeek(this.week_pick.year, this.week_pick.week);
      const first = getFirstDayOfWeek(d);
      const last = first + 6;
      // console.debug(first, last);
      const firstday = date.formatDate(
        new Date(d.setDate(first)).toDateString(),
        "YYYY/MM/DD"
      );
      const lastday = date.formatDate(
        new Date(d.setDate(last)).toDateString(),
        "YYYY/MM/DD"
      );
      this.date_picker = { from: firstday, to: lastday };
      console.debug("Datepicker upd: ", this.date_picker, this.week_pick.year);
    },
    parseDatePicker(): void {
      if (typeof this.date_picker != "string") {
        return;
      }
      console.debug("Parsing date: ", this.date_picker);
      const d = new Date(this.date_picker);
      console.debug(d, getWeekNumber(d));
      [this.week_pick.year, this.week_pick.week] = getWeekNumber(d);
      this.changeWeek(0);
    },
    // timeFormat(raw): string {
    //   return raw.slice(0, raw.length - 3);
    // },
    getDay(idx: number): string | undefined {
      if (!this.date_picker || typeof this.date_picker == "string") {
        return;
      }
      const fday = new Date(this.date_picker.from);
      // let fday = getDateOfISOWeek(this.week_pick.year, this.week_pick.week);
      const day = fday.getDay();
      fday.setDate(fday.getDate() + day + idx - 1);
      return date.formatDate(fday, "DD.MM");
    },
  },
});
</script>
