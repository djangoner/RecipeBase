<template>
  <q-item
    v-if="store.enableWebsocket"
    class="text-center text-white q-py-xs"
    :class="[websocketStateBg]"
    style="min-height: auto"
  >
    <q-item-section class="q-py-none">
      {{ websocketStateStr }}
      <q-tooltip> Обновление данных в режиме RealTime </q-tooltip>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { useBaseStore } from "src/stores/base"
import { websocketState } from "src/boot/websocketsRealtime"
import { computed } from "vue"

const store = useBaseStore()

const websocketStateBg = computed(() => {
  switch (websocketState.value) {
    case true:
      return "bg-green"
    case false:
      return "bg-red"
    default:
      return "bg-orange"
  }
})

const websocketStateStr = computed(() => {
  switch (websocketState.value) {
    case true:
      return "Ок"
    case false:
      return "Нет подключения"
    default:
      return "Подключение..."
  }
})
</script>
