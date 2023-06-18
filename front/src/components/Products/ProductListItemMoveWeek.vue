<template>
  <q-dialog
    v-model="showMoveWeek"
    persistent
  >
    <q-card style="min-width: 350px">
      <q-card-section>
        <div class="text-h6">
          Перенести задачу на другую неделю
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-select
          v-model="moveWeek"
          label="Неделя для переноса"
          :input-debounce="300"
          :options="weeksList || []"
          :option-label="(w) => w.year + '.' + w.week"
          use-input
          clearable
          options-dense
          dense
          autofocus
          @filter="filterWeeks"
        />

        <div class="q-mt-md row justify-around">
          <q-btn
            class="move-prev"
            label="Прошлая"
            icon="navigate_before"
            color="primary"
            size="sm"
            @click="moveWeekDelta(-1)"
          />
          <q-btn
            class="move-next"
            label="Следующая"
            icon="navigate_next"
            color="primary"
            size="sm"
            @click="moveWeekDelta(1)"
          />
        </div>
      </q-card-section>

      <q-card-actions
        align="right"
        class="text-primary"
      >
        <q-btn
          v-close-popup
          flat
          label="Отменить"
        />
        <q-btn
          class="btn-move"
          flat
          label="Перенести"
          @click="itemMoveWeek()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-btn
    v-if="isOnline && canEdit"
    label="Перенести на неделю..."
    icon="swap_horiz"
    size="sm"
    color="primary"
    no-caps
    dense
    unelevated
    @click="
      onOpenMove()
    "
  />
</template>

<script setup lang="ts">
import { ProductListWeekRead } from "src/client"
import { YearWeek } from "src/modules/Globals"
import { isOnline } from "src/modules/isOnline"
import { weekDelta } from "src/modules/WeekUtils"
import { useBaseStore } from "src/stores/base"
import { computed, PropType, Ref, ref, watch } from "vue"

const props = defineProps({
  modelValue: {
    type: Number,
    required: true,
  },
  week: { required: true, type: Object as PropType<YearWeek> },
  canEdit: {
    type: Boolean,
    default: false,
  },
})
const $emit = defineEmits(["update:model-value"])
const store = useBaseStore()

const showMoveWeek = ref(false)
const moveWeek: Ref<ProductListWeekRead | null> = ref(null)
const searchWeek = ref("")

const weeksList = computed(() => {
  // return Object.freeze(store?.product_lists)
  return store.product_lists
})

function onOpenMove(){
  showMoveWeek.value = true
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  filterWeeks('', () => {})
}

function filterWeeks(val: string, update: CallableFunction) {
  if (searchWeek.value == val && weeksList.value) {
    update();
    return;
  }
  searchWeek.value = val || ""
  const payload = {
    fields: "year,week,id",
    search: searchWeek.value.replaceAll(".", ""),
  }

  store
    .loadProductListWeeks(payload)
    .then(() => {
      update()
    })
    .catch(() => {
      update()
    })
}

async function moveWeekDelta(delta: number) {
  const year = props.week.year.valueOf()
  const week = props.week.week.valueOf()

  const payload = Object.assign({}, weekDelta(year, week, delta),{
    year: year,
    week: week,
  })
  const resp = await store.loadProductListWeek(payload, true)

  moveWeek.value = resp
    // delete moveWeek['items'];
}

function itemMoveWeek() {
  if (!moveWeek.value) {
    return
  }
  $emit("update:model-value", moveWeek.value.id)
  showMoveWeek.value = false
}

watch(() => props.modelValue, () => {
  showMoveWeek.value = false
})

</script>
