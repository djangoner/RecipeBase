<template>
  <week-select v-model="week" @update:modelValue="loadWeekPlan()" />
  <q-linear-progress
    :value="fillingPrc"
    :indeterminate="saving"
    :instant-feedback="saving"
    :animation-speed="500"
  />
  <q-page padding>
    <div
      class="week-select-page row wrap items-start q-col-gutter-x-sm q-col-gutter-y-md"
    >
      <!-- :class="$q.screen.lt.md ? 'column' : ''" -->
      <template v-for="(day, idx) of WeekDays" :key="idx">
        <div v-if="idx > 0" class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3">
          <q-card
            class="row column justify-around q-px-xs q-py-sm full-height"
            :class="[
              idx >= 6 ? 'bg-grey-3' : '',
              WeekDaysColors[idx],
              isToday(getDay(idx - 1)) ? 'shadow-5' : '',
              `weekday-${idx}`,
            ]"
            style="min-height: 300px"
          >
            <q-card-section>
              <span class="text-h6" :class="isToday(getDay(idx - 1)) ? 'day-active' : ''">
                <b>{{ getDay(idx - 1) }}</b> {{ day }}
              </span>
            </q-card-section>

            <q-card-section>
              <div class="q-gutter-y-md" v-if="loading">
                <q-skeleton type="QInput" />
                <q-skeleton type="QInput" />
              </div>
              <div class="flex column" v-else>
                <template v-for="mtime of meal_time" :key="mtime.id">
                  <div
                    :set="(recipes = getRecipes(idx, mtime))"
                    v-if="getRecipes(idx, mtime)?.length > 0 || mtime.is_primary"
                  >
                    <div
                      class="row q-col-gutter-x-sm wrap"
                      v-for="(recipe, rec_idx) of recipes"
                      :key="recipe"
                    >
                      <div class="col-auto">
                        <span class="text-subtitle1 q-my-none">
                          {{ mtime.title }}
                          <q-icon
                            v-if="recipe?.comment"
                            name="notes"
                            size="xs"
                            color="primary"
                          >
                            <q-tooltip class="full-width">
                              Комментарий:
                              {{ recipe?.comment }}
                            </q-tooltip>
                          </q-icon>
                          <q-tooltip>
                            {{ mtime.title }} - {{ timeFormat(mtime.time) }}
                          </q-tooltip>
                        </span>
                      </div>

                      <div class="col">
                        <q-select
                          :model-value="recipe"
                          @update:modelValue="setRecipe(idx, mtime, $event, rec_idx)"
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

                      <div class="flex flex-center col-auto" v-if="recipe">
                        <q-btn
                          :to="{ name: 'recipe', params: { id: recipe.id } }"
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
                        class="flex flex-center col-auto"
                        v-else-if="!mtime.is_primary"
                      >
                        <q-btn
                          @click="delPlan(idx, mtime)"
                          icon="close"
                          size="sm"
                          flat
                          dense
                          round
                        >
                          <q-tooltip>Убрать</q-tooltip>
                        </q-btn>
                      </div>

                      <recipe-card-tooltip
                        v-if="recipe && $q.screen.gt.xs"
                        :recipe="recipe"
                      ></recipe-card-tooltip>
                    </div>
                  </div>
                </template>
              </div>
            </q-card-section>
            <q-space />

            <q-card-section>
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
            </q-card-section>
          </q-card>
        </div>
      </template>
    </div>
  </q-page>
  <q-inner-loading :showing="loading"></q-inner-loading>
</template>

<script>
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
  getYearWeek,
} from 'components/WeekSelect.vue';
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';
import recipeCardTooltip from 'components/RecipeCardTooltip.vue';

let WeekDaysColors = {
  1: 'bg-amber-2',
  2: 'bg-cyan-3',
  3: 'bg-light-blue-3',
  4: 'bg-blue-4',
  5: 'bg-indigo-3',
};

export default {
  components: { weekSelect, recipeCardTooltip },
  data() {
    const store = useBaseStore();
    return {
      store,
      // week: {
      //   year: null,
      //   week: null,
      // },
      loading: false,
      saving: false,
      addMtimeSelect: null,
      meal_time_options: [],
      search: '',
      WeekDays,
      WeekDaysColors,
    };
  },
  mounted() {
    this.loadMealTime();
  },
  methods: {
    loadWeekPlan() {
      if (!this.week?.year || !this.week?.week) {
        return;
      }
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
      // let payload = Object.assign({}, this.plan);
      let payload = JSON.parse(JSON.stringify(this.plan));
      this.saving = true;

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
          this.saving = false;
        })
        .catch((err) => {
          this.saving = false;
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
            this.handleErrors(err, 'Ошибка загрузки рецептов');
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
          (v) => !v.is_primary && v.title.toLowerCase().indexOf(needle) > -1
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
    getRecipes(day, mtime) {
      if (!this.plan) {
        return;
      }
      let recipes = this.plan?.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id;
      });

      if (mtime.is_primary) {
        if (recipes.length < 1) {
          return [null];
        }
      }
      return recipes.map((r) => r.recipe);
    },
    setRecipe(day, mtime, value, rec_idx) {
      console.debug('setRecipe: ', day, mtime, value);
      let plans = this.plan.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id;
      });

      let plan = plans[rec_idx || 0];
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
    delPlan(idx, mtime) {
      console.debug('delPlan: ', idx, mtime, this.plan.plans);
      let delOne = false;
      this.plan.plans = this.plan.plans.filter((p) => {
        let r = p.day != idx || p.meal_time != mtime || p.recipe != null;
        if (!r && !delOne) {
          delOne = true;
          return false;
        }

        return true;
      });
    },

    timeFormat(raw) {
      return raw.slice(0, raw.length - 3);
    },
    getDay(idx) {
      let fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx);
      return date.formatDate(fday, 'DD.MM');
    },
    isToday(day) {
      let d = new Date();
      let d_str = d.getDate() + '.' + (d.getMonth() + 1).toString().padStart(2, '0');
      return day == d_str;
      // return day.getUTCDate() == new Date().getUTCDate();
    },
  },
  computed: {
    week: {
      get() {
        return { year: this.$query?.year, week: this.$query?.week };
      },
      set(val) {
        this.$query.year = val?.year;
        this.$query.week = val?.week;
      },
    },
    plan() {
      return this.store.week_plan;
    },
    meal_time() {
      return this.store.meal_time?.results;
    },
    recipesList() {
      return this.store.recipes?.results;
    },
    fillingPrc() {
      if (!this.meal_time) {
        return;
      }
      let plans = this.store.week_plan?.plans;
      let plansFilled;
      if (plans) {
        plansFilled = plans.filter((p) => p.meal_time.is_primary).length;
      }
      let plansTotal = this.meal_time.filter((m) => m.is_primary).length * 5;

      if (!plansFilled || !plansTotal) {
        return 0;
      }

      return plansFilled / plansTotal;
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

<style lang="scss">
.day-active {
  text-decoration: underline;
}

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
</style>
