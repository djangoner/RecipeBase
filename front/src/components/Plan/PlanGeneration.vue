<template>
  <base-dialog
    v-model="showDialog"
    title="Заполнение плана"
    :card-style="'width: 1000px;'"
  >
    <div
      class="row q-col-gutter-md justify-around"
      style="min-height: 700px"
    >
      <div class="col-12 col-md-6">
        <q-card
          class="row column"
          flat
          bordered
          style="min-height: 600px"
        >
          <q-card-section class="q-pa-none">
            <div class="text-subtitle1 text-center q-my-md">
              Добавить в план
              <small class="text-grey"> ({{ countNow }} / {{ countLimit }}) </small>
              <q-btn
                v-if="canAdd"
                icon="add"
                size="sm"
                color="positive"
                dense
                round
                unelevated
                @click="showSelectRecipe = true"
              />
            </div>
            <plan-gen-drag />

            <!-- <div
              v-if="canAdd"
              class="q-px-md q-my-sm"
            >
              <q-btn
                label="Выбрать рецепт"
                icon="add"
                color="positive"
                size="sm"
                unelevated
                no-caps
                @click="showSelectRecipe = true"
              />
            </div> -->
          </q-card-section>

          <q-space />

          <q-card-actions align="around">
            <q-btn
              icon="refresh"
              label="Сбросить"
              color="negative"
              no-caps
              unelevated
              :disable="recipesSelected.length < 1"
              @click="askReset"
            />
            <q-btn
              icon="save"
              label="Заполнить план"
              color="primary"
              no-caps
              unelevated
              :loading="isSaving"
              @click="fillPlan"
            />
          </q-card-actions>
        </q-card>
      </div>
      <div class="col-12 col-md-6">
        <q-card
          flat
          bordered
        >
          <!-- <div class="text-subtitle1 text-center q-my-md">
            Рекомендации
          </div> -->
          <plan-gen-recommendations
            :exclude="excludeIds"
            @add="onAdd"
          />
        </q-card>
      </div>
    </div>
  </base-dialog>

  <select-recipe-dialog
    v-model="showSelectRecipe"
    @select="onAdd"
  />

  <q-btn
    label="Заполнение"
    icon="tune"
    size="sm"
    color="secondary"
    no-caps
    dense
    @click="showDialog = true"
  />
</template>

<script setup lang="ts">
import PlanGenDrag from './PlanGenDrag.vue'
import SelectRecipeDialog from './SelectRecipeDialog.vue'
import PlanGenRecommendations from "./PlanGenRecommendations.vue"
import PlanRecipesDrag from "./PlanRecipesDrag.vue"
import BaseDialog from "../common/BaseDialog.vue"
import { computed, PropType, Ref, ref } from "vue"
import { useLocalStorage } from "@vueuse/core"
import { RecipeShort } from "src/client"
import { useBaseStore } from "src/stores/base"
import { storeToRefs } from "pinia"
import { YearWeek } from "src/modules/Globals"
import { promiseSetLoading } from "src/modules/StoreCrud"
import { useQuasar } from "quasar"
import { useLocalStore } from 'src/stores/local'

const props = defineProps({
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  },
})

const emit = defineEmits(["updated"])
const $q = useQuasar()


const store = useBaseStore()
const storeLocal = useLocalStore()
const {recipesSelected} = storeToRefs(storeLocal)
const { meal_time, week_plan } = storeToRefs(store)

const showDialog = ref(false)
const showSelectRecipe = ref(false)
const isSaving = ref(false)

const countNow = computed(() => recipesSelected.value.length)
const countLimit = computed(() => {
  if (!meal_time.value) {
    return 0
  }
  const plansTotal = meal_time.value.filter((m) => m.is_primary).length * 5
  const plansFilled = week_plan.value?.plans.filter((p) => p.meal_time.is_primary && p.day < 6).length

  return plansTotal - plansFilled
})

const canAdd = computed(() => countNow.value < countLimit.value)

const selectedIds = computed(() => recipesSelected.value.map((el) => el.id))
const filledIds = computed(() => {
  if (week_plan.value) {
    return week_plan.value.plans.map((el) => el.id)
  }
  return []
})

const excludeIds = computed(() => [].concat(selectedIds.value, filledIds.value))

function onAdd(recipe: RecipeShort) {
  storeLocal.recipesSelectedAdd(recipe)
}

function reset() {
  recipesSelected.value = [] as RecipeShort[]
}

function askReset() {
  $q.dialog({
    title: "Подтверждение",
    message: `Вы уверены что хотите сбросить список?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    reset()
  })
}

function fillPlan() {
  const prom = store.weekPlaceRecipes({ year: props.week.year, week: props.week.week, recipes: selectedIds.value })
  promiseSetLoading(prom, isSaving)
  void prom.then(() => {
    emit("updated")
    reset()
    showDialog.value = false
  })
}
</script>
