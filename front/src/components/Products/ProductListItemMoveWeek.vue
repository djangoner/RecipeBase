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
          :model-value="moveWeek"
          label="Неделя для переноса"
          :input-debounce="100"
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
            label="Прошлая"
            icon="navigate_before"
            color="primary"
            size="sm"
            @click="moveWeekDelta(-1)"
          />
          <q-btn
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
    @click="
      onOpenMove()
    "
  />
</template>

<script setup lang="ts">
import { ProductListItemRead, ProductListWeekRead } from "src/client"
import { YearWeek } from "src/modules/Globals"
import { useBaseStore } from "src/stores/base"
import { computed, PropType, Ref, ref, watch } from "vue"

const props = defineProps({
  item: {
    type: Object as PropType<ProductListItemRead>,
    required: true,
  },
  week: { required: true, type: Object as PropType<YearWeek> },
  canEdit: {
    type: Boolean,
    default: false,
  },
})
const $emit = defineEmits(["update:modelValue", "update:item"])
const store = useBaseStore()

const showMoveWeek = ref(false)
const moveWeek: Ref<ProductListWeekRead | null> = ref(null)
const searchWeek = ref("")

const isOnline = computed(() => {
  return navigator.onLine
})

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
  if (searchWeek.value == val) {
    update();
    return;
  }
  searchWeek.value = val || ""
  const payload = {
    short: "1",
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

function moveWeekDelta(delta: number) {
  const year = props.week.year.valueOf()
  let week = props.week.week.valueOf()

  week = week + delta

  if (week < 0) {
    week = 54
  } else if (week > 54) {
    week = 1
  }

  const payload = {
    year: year,
    week: week,
  }
  void store.loadProductListWeek(payload, true).then((resp) => {
    moveWeek.value = resp
    // delete moveWeek['items'];
  })
}

function itemMoveWeek() {
  if (!moveWeek.value) {
    return
  }

  const item = Object.assign({}, props.item)

  item.week = moveWeek.value.id
  $emit("update:item", item, true)
  showMoveWeek.value = false
}

watch(props.item, () => {
  showMoveWeek.value = false
})

</script>
