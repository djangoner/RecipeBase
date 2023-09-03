<template>
  <q-menu
    context-menu
    @before-show="preloadMenu()"
  >
    <q-list dense>
      <!-- Add to plan -->
      <q-item
        clickable
        @click="addToPlanPreload()"
      >
        <q-item-section side>
          <q-icon name="calendar_month" />
        </q-item-section>
        <q-item-section>Добавить в план</q-item-section>
        <q-item-section side>
          <q-icon name="keyboard_arrow_right" />
        </q-item-section>

        <q-menu
          anchor="top end"
          self="top start"
        >
          <q-list dense>
            <template v-for="(day, idx) of WeekDays">
              <q-item
                v-if="idx > 0"
                :key="idx"
                clickable
              >
                <q-item-section :class="isDayFilled(Number(idx)) ? 'text-underline text-bold' : ''">
                  {{ day }}
                </q-item-section>
                <q-item-section side>
                  <q-icon name="keyboard_arrow_right" />
                </q-item-section>

                <q-menu
                  auto-close
                  anchor="top end"
                  self="top start"
                >
                  <q-list dense>
                    <q-item
                      v-for="mtime of meal_time"
                      :key="mtime.id"
                      v-close-popup
                      clickable
                      @click="addToPlan(idx, mtime, recipe)"
                    >
                      <q-item-section :class="isMtimeFilled(idx, mtime) ? 'text-underline text-bold' : ''">
                        {{ mtime.title }}
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-item>
            </template>
          </q-list>
        </q-menu>
      </q-item>

      <!-- Archive management -->
      <q-item
        clickable
        @click="actionArchive()"
      >
        <q-item-section side>
          <q-icon name="archive" />
        </q-item-section>
        <q-item-section>
          <template v-if="recipe.is_archived">
            Убрать из архива
          </template><template v-else>
            В архив
          </template>
        </q-item-section>
      </q-item>
    </q-list>
  </q-menu>
</template>

<script lang="ts" setup>
import { getYearWeek, WeekDays, YearWeek } from "src/modules/WeekUtils"
import { useBaseStore } from "src/stores/base"
import { computed, ComputedRef, defineComponent, PropType } from "vue"
import { MealTime, RecipePlan, RecipeRead } from "src/client"
import HandleErrorsMixin, { CustomAxiosError, handleErrors } from "src/modules/HandleErrorsMixin"
import { useQuasar } from "quasar"
import { getCachedRecipe, loadCachedRecipe } from "src/modules/Cache"
import { storeToRefs } from "pinia"

const props = defineProps({
  recipe: { required: true, type: Object as PropType<RecipeRead> },
  loadRecipe: { type: Boolean, default: true },
})

const $emit = defineEmits(["updateItem"])
const $q = useQuasar()

const store = useBaseStore()
const {week_plan} = storeToRefs(store)
const [year, week] = getYearWeek()
// const week_p: YearWeek = {
//   year: year,
//   week: week,
// }

const meal_time = computed(() => {
  return store.meal_time
})


const recipe: ComputedRef<RecipeRead> = computed(() => {
  return getCachedRecipe(props.recipe)
})

function emitUpdated() {
  $emit("updateItem")
}
function actionArchive() {
  const recipe_title: string = recipe.value?.title || ""
  $q.dialog({
    title: "Подтверждение",
    message: recipe.value.is_archived ? `Вы уверены что хотите убрать рецепт '${recipe_title}' из архива?` : `Вы уверены что хотите перевести рецепт '${recipe_title}' в архив?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    const patchRecipe = {
      is_archived: !recipe.value.is_archived,
    }
    store
      .patchRecipe(recipe.value.id, patchRecipe)
      .then(() => {
        emitUpdated()
      })
      .catch((err: CustomAxiosError) => {
        handleErrors(err, "Ошибка сохранения рецепта")
      })
  })
}
function addToPlan(day: number, mtime: MealTime, recipe: RecipeRead) {
  console.debug("Add to plan: ", day, mtime, recipe)
  $q.dialog({
    title: "Подтверждение",
    message: `Добавить '${recipe?.title}' на '${mtime?.title}' в  ${WeekDays[day]}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    // Load current plan
    await loadWeekPlan()
    if (!week_plan.value){
      return
    }

    // @ts-expect-error New recipe plan
    const newPlanItem: RecipePlan = {
      week: week_plan.value.id,
      day: day,
      meal_time: mtime.id,
      recipe: recipe.id,
    }
    const prom = store.createWeekPlanItem(newPlanItem)
    const notif = $q.notify({
      group: false,
      timeout: 0,
      spinner: true,
      message: "Добавление в план..."
    })
      void prom.then(() => {
        notif({
          type: 'positive',
          message: 'Успешно добавлено в план',
          spinner: false,
          timeout: 2500,
        })
        void loadWeekPlan()
      }).catch(() => {
        notif({
          timeout: 1
        })
      })
  })
}

function addToPlanPreload() {
  if (!meal_time.value) {
    loadMealTime()
  }
  if (!week_plan.value) {
    void loadWeekPlan()
  }
}

function isDayFilled(day: number): boolean {
  const plans = week_plan.value?.plans
  const plansFilled = plans?.filter((p) => p.meal_time.is_primary && p.day === day).length || 0
  const mealTimesTotal = meal_time.value?.filter((m) => m.is_primary).length || 0

  return plansFilled >= mealTimesTotal && mealTimesTotal > 0
}
function isMtimeFilled(day: number, mtime: MealTime): boolean {
  const plans = week_plan.value?.plans
  const plansFilled = plans?.filter((p) => p.meal_time.id == mtime.id && p.day == day).length || 0
  return plansFilled > 0
}

//
function loadWeekPlan(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!week || !year) {
      reject()
      return
    }
    const payload = {
      year: year,
      week: week,
    }
    store
      .loadWeekPlan(payload)
      .then(() => {
        resolve()
      })
      .catch((err: CustomAxiosError) => {
        reject(err)
        handleErrors(err, "Ошибка загрузки плана")
      })
  })
}
function loadMealTime() {
  const payload = {
    pageSize: 1000,
  }
  // loading = true;

  const prom = store.loadMealTime(payload)
}
function preloadMenu(){
  void loadCachedRecipe(props.recipe)
}
</script>
