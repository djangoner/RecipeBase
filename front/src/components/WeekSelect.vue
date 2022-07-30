<template>
  <q-bar>
    <div class="col text-bold">
      <div class="row justify-center items-center q-col-gutter-x-md">
        <q-btn icon="chevron_left" flat @click="changeWeek(-1)"></q-btn>
        <span class="cursor-pointer q-px-md"
          >{{ week_pick.year }}.{{ String(week_pick.week).padStart(2, '0') }} ({{
            getDay(0)
          }}
          - {{ getDay(6) }})
          <q-menu>
            <q-date v-model="date_picker" first-day-of-week="1"></q-date>
          </q-menu>
        </span>
        <q-btn icon="chevron_right" flat @click="changeWeek(+1)"></q-btn>
      </div>
    </div>
  </q-bar>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';
export function getWeekNumber(d) {
  // Copy date so don't modify original
  d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  // Set to nearest Thursday: current date + 4 - current day number
  // Make Sunday's day number 7
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  // Get first day of year
  var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  // Calculate full weeks to nearest Thursday
  var weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
  // Return array of year and week number
  return [d.getUTCFullYear(), weekNo];
}

export function getFirstDayOfWeek(d) {
  const date = new Date(d);
  const day = date.getDay();

  const diff = date.getDate() - day + (day === 0 ? -6 : 1);

  return diff;
  // return new Date(date.setDate(diff));
}

export function getDateOfISOWeek(y, w) {
  var simple = new Date(y, 0, 1 + (w - 1) * 7);
  var dow = simple.getDay();
  var ISOweekStart = simple;
  if (dow <= 4) ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
  else ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
  return ISOweekStart;
}

export let WeekDays = {
  0: 'Вс (прошлый)',
  1: 'Понедельник',
  2: 'Вторник',
  3: 'Среда',
  4: 'Четверг',
  5: 'Пятница',
  6: 'Суббота',
  7: 'Восскресенье',
};

export default {
  props: {
    modelValue: { required: true },
  },
  data() {
    const store = useBaseStore();
    return {
      store,
      date_picker: null,
      week_pick: {
        year: null,
        week: null,
      },
      WeekDays,
    };
  },
  mounted() {
    this.selectToday();
  },
  methods: {
    selectToday() {
      let [year, week] = getWeekNumber(new Date());
      this.week_pick.year = year;
      this.week_pick.week = week;
      this.changeWeek(0);
    },
    changeWeek(num) {
      let min = 1;
      let max = 53;

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
    updateDatePicker() {
      // let d = new Date();
      let d = getDateOfISOWeek(this.week_pick.year, this.week_pick.week);
      let first = getFirstDayOfWeek(d);
      let last = first + 6;
      // console.debug(first, last);
      let firstday = date.formatDate(
        new Date(d.setDate(first)).toDateString(),
        'YYYY/MM/DD'
      );
      let lastday = date.formatDate(
        new Date(d.setDate(last)).toDateString(),
        'YYYY/MM/DD'
      );
      this.date_picker = { from: firstday, to: lastday };
      console.debug('Datepicker upd: ', this.date_picker, this.week_pick.year, this.week);
    },
    parseDatePicker() {
      if (typeof this.date_picker != 'string') {
        return;
      }
      console.debug('Parsing date: ', this.date_picker);
      let d = new Date(this.date_picker);
      console.debug(d, getWeekNumber(d));
      [this.week_pick.year, this.week_pick.week] = getWeekNumber(d);
      this.changeWeek(0);
    },
    timeFormat(raw) {
      return raw.slice(0, raw.length - 3);
    },
    getDay(idx) {
      let fday = new Date(this?.date_picker?.from);
      let day = fday.getDay();
      fday.setDate(fday.getDate() + day + idx - 1);
      return date.formatDate(fday, 'DD.MM');
    },
  },
  watch: {
    date_picker(val, oldVal) {
      if (JSON.stringify(val) != JSON.stringify(oldVal)) {
        this.parseDatePicker();
      }
    },
    modelValue(val, oldVal) {
      console.debug('modelValue: ', val, oldVal);
      if (val !== oldVal) {
        this.week_pick = val;
      }
    },
    week_pick: {
      deep: true,
      handler: function (val, oldVal) {
        console.debug('week_pick: ', val, oldVal);
        this.$emit('update:modelValue', val);
      },
    },
  },
};
</script>
