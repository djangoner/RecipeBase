<template>
  <week-select v-model="week" @update:modelValue="loadWeekPlan()" />
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
                  :options="meal_time_options"
                  @update:modelValue="addMtime(idx, $event)"
                  @filter="filterMealTime"
                  :input-debounce="0"
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
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
} from 'components/WeekSelect.vue';
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';

export default {
  components: { weekSelect },
  data() {
    const store = useBaseStore();
    return {
      store,
      week: {
        year: null,
        week: null,
      },
      loading: false,
      addMtimeSelect: null,
      meal_time_options: [],
      search: '',
      WeekDays,
    };
  },
  mounted() {
    let [year, week] = getWeekNumber(new Date());
    this.week.year = year;
    this.week.week = week;
    this.loadMealTime();
  },
  methods: {
    loadWeekPlan() {
      let payload = {
        year: this.week.year,
        week: this.week.week,
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

    filterMealTime(val, update, abort) {
      update(() => {
        let isUsed = (mtime) => {
          //   // console.debug(ing, this.recipe.ingredients);
          return this.plan?.plans.some((plan) => {
            return plan.meal_time.id == mtime.id;
          });
          //   return this.recipe.ingredients.some((t) => t.ingredient.id == ing.id);
        };
        const needle = val.toLowerCase();

        this.meal_time_options = this.meal_time.filter(
          (v) => !v.is_primary && v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)
        );
        // console.debug(needle, this.tagList, tags);
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
      let fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, 'DD.MM');
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
