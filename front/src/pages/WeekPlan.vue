<template>
  <q-bar>
    <div class="col text-bold">
      <div class="row justify-center items-center q-col-gutter-x-md">
        <q-btn icon="chevron_left" flat @click="changeWeek(-1)"></q-btn>
        <span class="cursor-pointer q-px-md"
          >{{ year }}.{{ String(week).padStart(2, '0') }} ({{ getDay(0) }} -
          {{ getDay(6) }})
          <q-menu>
            <q-date v-model="date_picker" first-day-of-week="1"></q-date>
          </q-menu>
        </span>
        <q-btn icon="chevron_right" flat @click="changeWeek(+1)"></q-btn>
      </div>
    </div>
  </q-bar>
  <q-page padding>
    <div class="row wrap q-col-gutter-x-sm q-col-gutter-y-md">
      <!-- :class="$q.screen.lt.md ? 'column' : ''" -->
      <div
        class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3"
        v-for="(day, idx) of WeekDays"
        :key="idx"
      >
        <q-card
          class="row column justify-around q-px-xs q-py-sm full-height"
          :class="idx >= 6 ? 'bg-grey-3' : ''"
        >
          <q-card-section>
            <span class="text-h6">
              <b>{{ getDay(idx - 1) }}</b> {{ day }}
            </span>
          </q-card-section>

          <q-card-section>
            <div class="flex column">
              <template v-for="mtime of meal_time" :key="mtime.id">
                <div
                  class="row"
                  v-if="getRecipe(idx, mtime) !== undefined || mtime.is_primary"
                >
                  <div class="col">
                    <span class="text-subtitle1 q-my-none">
                      {{ mtime.title }}
                      <q-tooltip>
                        {{ mtime.title }} - {{ timeFormat(mtime.time) }}
                      </q-tooltip>
                    </span>
                  </div>

                  <div class="col">
                    <q-select
                      :model-value="getRecipe(idx, mtime)"
                      @update:modelValue="setRecipe(idx, mtime, $event)"
                      :input-debounce="100"
                      :options="recipesList"
                      option-label="title"
                      @filter="filterRecipes"
                      use-input
                      clearable
                      options-dense
                      dense
                    >
                      <template v-slot:no-option>
                        <q-item>
                          <q-item-section class="text-grey">
                            Нет результатов
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>
                    <!-- <span>{{ getRecipe(idx, mtime)?.title }}</span> -->
                  </div>
                </div>
              </template>

              <div class="row q-mt-sm">
                <q-select
                  class="col"
                  :modelValue="null"
                  :options="meal_time"
                  @update:modelValue="addMtime(idx, $event)"
                  option-value="id"
                  option-label="title"
                  label="Добавить"
                  map-options
                  use-input
                  options-dense
                  dense
                ></q-select>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
  <q-inner-loading :showing="loading"></q-inner-loading>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';

function getWeekNumber(d) {
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

function getFirstDayOfWeek(d) {
  const date = new Date(d);
  const day = date.getDay();

  const diff = date.getDate() - day + (day === 0 ? -6 : 1);

  return diff;
  // return new Date(date.setDate(diff));
}

function getDateOfISOWeek(y, w) {
  var simple = new Date(y, 0, 1 + (w - 1) * 7);
  var dow = simple.getDay();
  var ISOweekStart = simple;
  if (dow <= 4) ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
  else ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
  return ISOweekStart;
}

let WeekDays = {
  1: 'Понедельник',
  2: 'Вторник',
  3: 'Среда',
  4: 'Четверг',
  5: 'Пятница',
  6: 'Суббота',
  7: 'Восскресенье',
};

export default {
  data() {
    const store = useBaseStore();
    return {
      store,
      year: null,
      week: null,
      loading: false,
      date_picker: null,
      addMtimeSelect: null,
      search: '',
      WeekDays,
    };
  },
  mounted() {
    this.selectToday();
    // this.loadWeekPlan();
    this.loadMealTime();
  },
  methods: {
    selectToday() {
      let [year, week] = getWeekNumber(new Date());
      this.year = year;
      this.week = week;
      this.changeWeek(0);
    },
    loadWeekPlan() {
      let payload = {
        year: this.year,
        week: this.week,
      };
      this.loading = true;

      this.store
        .loadWeekPlan(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки плана');
        });
    },
    saveWeekPlan() {
      let payload = Object.assign({}, this.plan);
      this.loading = true;

      payload.plans.map((p) => {
        if (typeof p.recipe == 'object') {
          p.recipe = p.recipe?.id;
        }
        if (typeof p.meal_time == 'object') {
          p.meal_time = p.meal_time.id;
        }
      });

      payload.plans = payload.plans.filter((p) => {
        return p.recipe && p.meal_time;
      });

      console.debug('Save: ', payload);

      this.store
        .saveWeekPlan(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки плана');
        });
    },
    loadMealTime() {
      let payload = {
        page_size: 1000,
      };
      // this.loading = true;

      this.store
        .loadMealTime(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки времени приема пищи');
        });
    },
    loadRecipes() {
      return new Promise((resolve, reject) => {
        let payload = {
          search: this.search,
          // page_size: 1,
        };

        this.store
          .loadRecipes(payload)
          .then(() => {
            resolve(payload);
          })
          .catch((err) => {
            console.warn(err);
            reject(err);
            this.handleError(err, 'Ошибка загрузки рецептов');
          });
      });
    },
    changeWeek(num) {
      let min = 1;
      let max = 53;

      this.week += num;

      if (this.week < min) {
        this.week = max;
        this.year -= 1;
      } else if (this.week > max) {
        this.week = min;
        this.year += 1;
      }
      this.updateDatePicker();
      this.loadWeekPlan();
    },
    updateDatePicker() {
      // let d = new Date();
      let d = getDateOfISOWeek(this.year, this.week);
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
      console.debug('Datepicker upd: ', this.date_picker, this.year, this.week);
    },
    parseDatePicker() {
      if (typeof this.date_picker != 'string') {
        return;
      }
      console.debug('Parsing date: ', this.date_picker);
      let d = new Date(this.date_picker);
      console.debug(d, getWeekNumber(d));
      [this.year, this.week] = getWeekNumber(d);
      this.changeWeek(0);
    },

    filterRecipes(val, update, abort) {
      if (this.search == val && this.recipesList) {
        update(() => {});
        return;
      }
      this.search = val;
      this.loadRecipes()
        .then(() => {
          update(() => {});
        })
        .catch(() => {
          update(() => {});
        });
    },
    // Utils
    getRecipe(day, mtime) {
      if (!this.plan) {
        return;
      }
      let recipes = this.plan?.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id;
      });
      return recipes[0]?.recipe;
    },
    setRecipe(day, mtime, value) {
      console.debug('setRecipe: ', day, mtime, value);
      let plans = this.plan.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id;
      });

      let plan = plans[0];
      if (plan) {
        console.debug('Updating recipe...');
        plan.recipe = value;
        // this.plan.plans.map((p) => {
        //   if (p == recipe) {
        //     p = value;
        //   }
        //   return p;
        // });
      } else {
        this.plan.plans.push({
          // week: this.id,
          day: day,
          meal_time: mtime,
          recipe: value,
        });
      }
      this.saveWeekPlan();
    },
    addMtime(day_idx, mtime) {
      console.debug('addMtime: ', day_idx, mtime);
      this.plan.plans.push(
        Object.assign(
          {},
          {
            day: parseInt(day_idx),
            meal_time: mtime,
            recipe: null,
          }
        )
      );
    },

    timeFormat(raw) {
      return raw.slice(0, raw.length - 3);
    },
    getDay(idx) {
      let fday = new Date(this?.date_picker?.from);
      let day = fday.getDay();
      fday.setDate(fday.getDate() + day + idx - 1);
      return date.formatDate(fday, 'MM.DD');
    },
  },
  computed: {
    plan() {
      return this.store.week_plan;
    },
    meal_time() {
      return this.store.meal_time?.results;
    },
    recipesList() {
      return this.store.recipes?.results;
    },
  },
  watch: {
    date_picker(val, oldVal) {
      if (JSON.stringify(val) != JSON.stringify(oldVal)) {
        this.parseDatePicker();
      }
    },
  },
};
</script>
