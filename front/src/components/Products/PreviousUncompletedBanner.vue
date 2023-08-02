<template>
  <q-banner
    class="bg-info text-white"
    inline-actions
  >
    <template #avatar>
      <q-icon
        name="history"
        size="md"
      />
    </template>

    На прошлой неделе осталось {{ count }} не отмеченных продуктов

    <template #action>
      <q-btn
        label="Перенести"
        color="white"
        flat
        @click="askMoveUncompleted()"
      />
    </template>
    <q-inner-loading :showing="isLoading" />
  </q-banner>
</template>
>

<script setup lang="ts">
import { useQuasar } from "quasar"
import { useBaseStore } from "src/stores/base"
import { YearWeek } from "src/modules/Globals"
import { PropType, ref } from "vue"
import { promiseSetLoading } from "src/modules/StoreCrud"

const props = defineProps({
  count: {
    type: Number,
    default: 0,
  },
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  }
})

const $emit = defineEmits(["reload"])

const $q = useQuasar()
const store = useBaseStore()

const isLoading = ref(false)

function askMoveUncompleted() {
  $q.dialog({
    title: `Перенос списка продуктов`,
    message: `Вы уверены что хотите перенести ${props.count} продуктов на эту неделю?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    moveUncompleted()
  })
}

function moveUncompleted() {
  const prom = store.productListMoveUncompleted({year: props.week.year, week: props.week.week})

  promiseSetLoading(prom, isLoading)

  void prom.then(() => {
    $q.notify({
      type: "positive",
      caption: "Список продуктов успешно перенесен",
    })
    $emit("reload")
  })


}
</script>
