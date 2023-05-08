<template>
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
  <q-page
    id="week_plan_print"
    padding
  >
    <div class="row items-center q-col-gutter-x-md print-hide">
      <div>
        <q-toggle
          v-model="editMode"
          label="Режим редактирования"
          :readonly="!canEdit"
        />
      </div>
      <div>
        <q-btn
          icon="print"
          color="primary"
          size="sm"
          no-caps
          unelevated
          @click="onPrint()"
        >
          Распечатать план
        </q-btn>
      </div>
      <q-space />
      <div>
        <q-btn
          icon="menu"
          round
          dense
          flat
        >
          <q-menu>
            <q-list dense>
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
          <q-card
            class="row column justify-around q-px-xs q-py-sm full-height"
            :class="[
              idx >= 6 ? 'bg-grey-3 print-hide print-week-hide' : '',
              WeekDaysColors[idx],
              // isToday(getDay(idx - 1)) ? 'shadow-5' : '',
              `weekday-${idx}`,
            ]"
            style="min-height: 300px"
          >
            <q-card-section class="row justify-between">
              <span
                class="text-h6"
                :class="isToday(getDay(idx - 1)) ? 'day-active' : ''"
              >
                <b>{{ getDay(idx - 1) }}</b> {{ day }}
              </span>
              <q-btn
                v-if="plan?.comments"
                icon="announcement"
                :color="plan.comments[idx] ? 'red' : 'grey'"
                :disable="saving"
                flat
                round
                @click="openComment(idx)"
              >
                <q-tooltip v-if="plan.comments[idx]">
                  {{ plan.comments[idx] }}
                </q-tooltip>
              </q-btn>
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
                    v-if="getDayPlans(idx, mtime).length > 0 || mtime.is_primary"
                    :key="mtime.id"
                  >
                    <div
                      v-for="(dayPlan, rec_idx) of getDayPlans(idx, mtime)"
                      :key="rec_idx"
                      class="row q-col-gutter-x-sm wrap"
                    >
                      <div class="col-auto">
                        <div>
                          <span class="text-subtitle1 q-my-none relative-position q-py-xs">
                            {{ mtime.title }}
                            <q-badge
                              v-if="dayPlan && getWarning(dayPlan)"
                              :color="getWarningColor(dayPlan)"
                              rounded
                              floating
                            />
                          </span>
                          <q-icon
                            v-if="dayPlan?.recipe?.comment"
                            name="notes"
                            size="xs"
                            color="primary"
                          >
                            <q-tooltip
                              anchor="top middle"
                              self="bottom middle"
                              :offset="[10, 10]"
                            >
                              Комментарий:
                              {{ dayPlan?.recipe?.comment }}
                            </q-tooltip>
                          </q-icon>
                          <q-tooltip>
                            {{ mtime.title }} -
                            {{ timeFormat(mtime.time || null) }}
                          </q-tooltip>
                        </div>
                      </div>

                      <div class="col">
                        <recipe-select
                          :model-value="dayPlan?.recipe"
                          :readonly="readonly"
                          @update:model-value="setRecipe(idx, mtime, $event, rec_idx)"
                        />
                        <!-- <span>{{ getplan(idx, mtime)?.title }}</span> -->
                      </div>

                      <div
                        v-if="dayPlan?.recipe"
                        class="flex flex-center col-auto"
                      >
                        <q-btn
                          v-if="storeAuth.hasPerm('recipes.view_recipe')"
                          :to="{
                            name: 'recipe',
                            params: { id: dayPlan.recipe.id },
                          }"
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
                        v-else-if="!mtime.is_primary"
                        class="flex flex-center col-auto"
                      >
                        <q-btn
                          icon="close"
                          size="sm"
                          flat
                          dense
                          round
                          @click="delPlan(idx, mtime)"
                        >
                          <q-tooltip>Убрать</q-tooltip>
                        </q-btn>
                      </div>

                      <recipe-card-tooltip
                        v-if="dayPlan?.recipe && $q.screen.gt.xs"
                        :recipe="dayPlan.recipe"
                      />
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
                  :model-value="null"
                  :options="meal_time_options || []"
                  :input-debounce="0"
                  :readonly="readonly"
                  option-value="id"
                  option-label="title"
                  label="Добавить"
                  map-options
                  use-input
                  options-dense
                  dense
                  @update:model-value="addMtime(idx, $event)"
                  @filter="filterMealTime"
                />
              </div>
            </q-card-section>
          </q-card>
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
  </q-page>
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
  <div
    v-if="enableFireworks && showFireworks"
    class="position-absolute absolute-top-right toolbar-topright"
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

  <q-inner-loading :showing="loading" />
</template>

<script lang="ts">
import RecipeSelect from "../components/Recipes/RecipeSelect.vue"
import weekSelect from "components/WeekSelect.vue"
import { useBaseStore } from "src/stores/base"
import { date, LocalStorage } from "quasar"
import recipeCardTooltip from "components/RecipeCardTooltip.vue"
import PlanWeekInfo from "src/components/PlanWeekInfo.vue"
import { defineComponent, defineAsyncComponent } from "vue"
import { getDateOfISOWeek, YearWeek } from "src/modules/WeekUtils"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { WeekDays } from "src/modules/WeekUtils"
import { MealTime, RecipeRead, RecipePlanRead } from "src/client"
import { RecipePlanWeekFromRead } from "src/Convert"
import { useAuthStore } from "src/stores/auth"
// import VueHtmlToPaper from 'vue-html-to-paper';
import { Directive } from "vue"
import { WarningPriorities } from "src/modules/Globals"
import { getWarningPriorityColor } from "src/modules/Utils"
// import { useQuery } from "@oarepo/vue-query-synchronizer";
import IsOnlineMixin from "src/modules/IsOnlineMixin"
import Fireworks from "@fireworks-js/vue"

const WeekDaysColors: { [key: number]: string } = {
  1: "bg-amber-2",
  2: "bg-cyan-3",
  3: "bg-light-blue-3",
  4: "bg-blue-4",
  5: "bg-indigo-3",
}

type QueryInterface = YearWeek

interface PlanComments {
  [id: number]: string
}

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

export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { weekSelect, recipeCardTooltip, PlanWeekInfo, Fireworks, RecipeSelect }, // : defineAsyncComponent(() => import("@fireworks-js/vue"))
  directives: {
    print: print as Directive,
  },
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  data() {
    const store = useBaseStore()
    const storeAuth = useAuthStore()
    return {
      store,
      storeAuth,
      // $query: useQuery(),
      // week: {
      //   year: null,
      //   week: null,
      // },
      loading: false,
      editMode: null as boolean | null,
      saving: false,
      enableFireworks: Boolean(LocalStorage.getItem("enableFireworks")),
      showFireworks: false,
      fireworksOptions: fireworksOptions,
      addMtimeSelect: null,
      meal_time_options: [] as MealTime[] | null,
      WeekDays,
      WeekDaysColors,
    }
  },
  computed: {
    week: {
      get() {
        return {
          year: (this.$query as QueryInterface)?.year as string | number | null,
          week: (this.$query as QueryInterface)?.week as string | number | null,
        } as YearWeek
      },
      set(val: YearWeek) {
        ;(this.$query as QueryInterface).year = val?.year
        ;(this.$query as QueryInterface).week = val?.week
      },
    },
    readonly() {
      return this.saving || !this.editMode || !this.canEdit || !this.isOnLine
    },
    plan() {
      return this.store.week_plan
    },
    meal_time() {
      return this.store.meal_time
    },
    fillingPrc(): number | null {
      if (!this.meal_time) {
        return null
      }
      const plans = this.store.week_plan?.plans
      let plansFilled
      if (plans) {
        plansFilled = plans.filter((p) => p.meal_time.is_primary).length
      }
      const plansTotal = this.meal_time.filter((m) => m.is_primary).length * 5

      if (!plansFilled || !plansTotal) {
        return 0
      }

      return plansFilled / plansTotal
    },
    canEdit() {
      return this.storeAuth.hasPerm("recipes.change_recipeplanweek")
    },
    conditions() {
      return this.store.conditions
    },
    warnedPlans(): WarnedPlans {
      const warnings = this.plan?.warnings || []
      const res: WarnedPlans = {}

      for (const warning of warnings) {
        let cond = this.getCondition(warning.condition)
        const plan = warning.plan
        if (!Object.hasOwn(res, plan)) {
          cond = this.getCondition(warning.condition)
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
    },
    refFireworks() {
      return this.$refs.fw as InstanceType<typeof Fireworks>
    },
  },
  watch: {
    enableFireworks(val: boolean) {
      LocalStorage.set("enableFireworks", val)
    },
    showFireworks(val: boolean) {
      if (this.enableFireworks) {
        if (val) {
          document.documentElement.classList.add("no-scroll")
        } else {
          document.documentElement.classList.remove("no-scroll")
        }
      }
    },
    fillingPrc(val, oldVal) {
      // When plan finished, show fireworks if enabled
      if (val == 1 && oldVal && oldVal !== 1) {
        this.showFireworks = true
      }
    },
  },
  created() {
    void this.$nextTick(() => {
      this.loadMealTime()
    })
  },
  methods: {
    onPrint() {
      console.debug("Print before")
      this.store.printMode = true
      void this.$nextTick(() => {
        window.print()
        this.store.printMode = false
        console.debug("Print after")
      })
    },
    loadWeekPlan() {
      if (!this.week?.year || !this.week?.week) {
        return
      }
      const payload = {
        year: this.week.year,
        week: this.week.week,
      }
      this.loading = true

      this.store
        .loadWeekPlan(payload)
        .then(() => {
          this.loading = false
          if (this.editMode === null) {
            this.editMode = !(this.plan?.plans && this.plan?.plans?.length > 0)
          }
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки плана")
        })
    },
    saveWeekPlan() {
      // let payload = Object.assign({}, this.plan);
      const payload = RecipePlanWeekFromRead(Object.assign({}, this.plan))
      this.saving = true
      console.debug("Save: ", payload)

      this.store
        .saveWeekPlan(payload)
        .then(() => {
          this.saving = false
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false
          this.handleErrors(err, "Ошибка загрузки плана")
        })
    },
    loadMealTime() {
      const payload = {
        pageSize: 1000,
      }
      // this.loading = true;

      this.store
        .loadMealTime(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, "Ошибка загрузки времени приема пищи")
        })
    },

    filterMealTime(val: string, update: CallableFunction) {
      update(() => {
        // let isUsed = (mtime: MealTime) => {
        //   //   // console.debug(ing, this.recipe.ingredients);
        //   return this.plan?.plans.some((plan) => {
        //     return plan.meal_time.id == mtime.id;
        //   });
        //   //   return this.recipe.ingredients.some((t) => t.ingredient.id == ing.id);
        // };
        const needle = val.toLowerCase()

        this.meal_time_options = this.meal_time?.filter((v) => !v.is_primary && v.title.toLowerCase().indexOf(needle) > -1) || []
        // console.debug(needle, this.tagList, tags);
      })
    },
    // Utils
    getRecipe(day: number, mtime: MealTime) {
      if (!this.plan) {
        return
      }
      const recipes = this.plan?.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id
      })
      return recipes[0]?.recipe
    },
    getDayPlans(day: number, mtime: MealTime) {
      if (!this.plan) {
        return []
      }
      const plans = this.plan?.plans.filter((plan) => {
        return plan.day == day && plan.meal_time.id == mtime.id
      })

      if (mtime.is_primary) {
        if (plans.length < 1) {
          return [null]
        }
      }
      return plans //.map((r) => r.recipe);
    },
    setRecipe(day: number, mtime: MealTime, value: RecipeRead, rec_idx?: number) {
      console.debug("setRecipe: ", day, mtime, value)
      const plans =
        this.plan?.plans?.filter((plan) => {
          return plan.day == day && plan.meal_time.id == mtime.id
        }) || []

      const plan = plans[rec_idx || 0]
      if (plan) {
        console.debug("Updating recipe...")
        plan.recipe = value
        // this.plan.plans.map((p) => {
        //   if (p == recipe) {
        //     p = value;
        //   }
        //   return p;
        // });
      } else {
        // @ts-expect-error: Plan will be created
        this.plan.plans.push({
          // week: this.id,
          day: day,
          meal_time: mtime,
          recipe: value,
        })
      }
      this.saveWeekPlan()
    },
    addMtime(day_idx: string | number, mtime: MealTime) {
      console.debug("addMtime: ", day_idx, mtime)
      this.plan?.plans?.push(
        // @ts-expect-error: Meal time will be added
        Object.assign(
          {},
          {
            day: typeof day_idx == "number" ? day_idx : parseInt(day_idx),
            meal_time: mtime,
            recipe: null,
          }
        )
      )
    },
    delPlan(idx: number, mtime: MealTime) {
      if (!this.plan || !this.plan.plans) {
        return
      }
      console.debug("delPlan: ", idx, mtime, this.plan?.plans)
      let delOne = false
      this.plan.plans =
        this.plan?.plans?.filter((p) => {
          const r = p.day != idx || p.meal_time != mtime || p.recipe != null
          if (!r && !delOne) {
            delOne = true
            return false
          }

          return true
        }) || []
    },

    openComment(idx: number) {
      if (!this.plan) {
        return
      }
      if (!this.plan?.comments) {
        this.plan.comments = {}
      }
      const comments = this.plan?.comments as PlanComments
      const startPlanID = this.plan.id

      this.$q
        .dialog({
          title: `Комментарий - ${this.getDay(idx - 1)}. ${WeekDays[idx]}`,
          prompt: {
            model: comments[idx],
            type: "textarea",
            autogrow: true,
            inputStyle: { minHeight: "3rem", maxHeight: "10rem" },
            readonly: !this.editMode,
          },
          cancel: true,
          persistent: true,
        })
        .onOk((comment: string) => {
          if (!this.plan || this.plan.id !== startPlanID) {
            console.debug("Comment update invalidated")
            return
          }
          if (!this.editMode || !this.canEdit) {
            return
          }
          ;(this.plan.comments as PlanComments)[idx] = comment
          this.saveWeekPlan()
        })
    },

    timeFormat(raw: string | null) {
      if (!raw) {
        return raw
      }
      return raw.slice(0, raw.length - 3)
    },
    getDay(idx: number): string {
      const fday = getDateOfISOWeek(this.week.year, this.week.week)
      fday.setDate(fday.getDate() + idx)
      return date.formatDate(fday, "DD.MM")
    },
    isToday(day: string) {
      const d = new Date()
      const d_str = String(d.getDate()) + "." + (d.getMonth() + 1).toString().padStart(2, "0")
      return day == d_str
      // return day.getUTCDate() == new Date().getUTCDate();
    },
    getWarning(plan: RecipePlanRead) {
      return this.warnedPlans[plan.id] || null
    },
    getWarningColor(plan: RecipePlanRead) {
      const warn = this.getWarning(plan)
      return getWarningPriorityColor(warn.priority)
    },
    getCondition(id: number) {
      return this.conditions?.find((c) => c.id == id) || null
    },
  },
})
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

.toolbar-topright {
  z-index: 99999;
}
</style>
