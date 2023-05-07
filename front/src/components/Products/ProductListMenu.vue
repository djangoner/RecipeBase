<template>
  <q-btn
    icon="menu"
    size="md"
    flat
    round
    dense
  >
    <q-menu>
      <q-list dense>
        <q-item
          v-ripple
          tag="label"
        >
          <q-item-section side>
            <q-toggle
              :model-value="markAlreadyCompleted"
              dense
              @update:model-value="$emit('update:markAlreadyCompleted', $event)"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>Отметить что уже есть</q-item-label>
          </q-item-section>
        </q-item>
        <q-item
          v-ripple
          tag="label"
        >
          <q-item-section side>
            <q-toggle
              :model-value="showAlreadyCompleted"
              dense
              @update:model-value="$emit('update:showAlreadyCompleted', $event)"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>Показать продукты уже есть</q-item-label>
          </q-item-section>
        </q-item>

        <q-item
          v-if="storeAuth.hasPerm('recipes.change_productlistitem')"
          :disable="!isOnline"
          clickable
          @click="regenerateList()"
        >
          <q-item-section avatar>
            <q-icon
              name="refresh"
              color="primary"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label> Обновить автоматический список </q-item-label>
          </q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('recipes.change_productlistitem')"
          :disable="!canSync"
          :class="[canSync ? 'bg-green text-white' : '']"
          clickable
          @click="$emit('askSync')"
        >
          <q-item-section avatar>
            <q-icon
              name="sync"
              color="primary"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label> Синхронизация </q-item-label>
          </q-item-section>
        </q-item>
        <q-item
          clickable
          @click="askClearDB()"
        >
          <q-item-section avatar>
            <q-icon
              name="delete"
              color="negative"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label> Очистить локальную БД </q-item-label>
          </q-item-section>
        </q-item>

        <q-item
          v-close-popup
          clickable
          @click="sendList()"
        >
          <q-item-section avatar>
            <q-icon name="send" />
          </q-item-section>
          <q-item-section>
            <q-item-label> Отправить в телеграмм </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </q-btn>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar"
import { YearWeek } from "src/modules/Globals"
import { CustomAxiosError, handleErrors } from "src/modules/HandleErrorsMixin"
import { useBaseStore } from "src/stores/base"
import { computed, PropType } from "vue"
import { destroyDB, productListUpdateFromServer } from "src/modules/ProductListSync"
import { useAuthStore } from "src/stores/auth"

const props = defineProps({
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  },
  showAlreadyCompleted: {
    type: Boolean,
    default: false,
  },
  markAlreadyCompleted: {
    type: Boolean,
    default: false,
  },
  canSync: {
    type: Boolean,
    default: false,
  },
})

const $emit = defineEmits(["loading", "askSync", "dialogObj", "update:markAlreadyCompleted", "update:showAlreadyCompleted", "canSyncFlag"])

const $q = useQuasar()
const store = useBaseStore()
const storeAuth = useAuthStore()

const isOnline = computed(() => navigator.onLine)

function sendList() {
  const payload = {
    year: props.week?.year,
    week: props.week?.week,
  }
  $q.loading.show({
    group: "sending",
    message: "Отправка списка...",
    delay: 400, // ms
  })

  store
    .productListSend(payload)
    .then(() => {
      $q.loading.hide("sending")
      $q.notify({
        type: "positive",
        message: `Список успешно отправлен`,
      })
    })
    .catch((err: CustomAxiosError) => {
      $q.loading.hide("sending")
      handleErrors(err, "Ошибка отправки списка")
    })
}

function regenerateList() {
  if (!props.week.year || !props.week.week) {
    return
  }
  const payload = {
    year: props.week.year,
    week: props.week.week,
  }
  $emit("loading", true)

  store
    .generateProductListWeek(payload)
    .then((resp) => {
      $emit("loading", false)
      void productListUpdateFromServer(resp)
    })
    .catch(() => {
      $emit("loading", false)
    })
}

function askClearDB() {
  const dialog = $q
    .dialog({
      title: "Подтверждение",
      message: `Вы уверены что хотите удалить локальные данные синхронизации? Это действие необратимо, локальный список продуктов будет стерт.`,
      cancel: true,
      persistent: true,
    })
    .onOk(() => {
      void runClearDB()
    })
  $emit("dialogObj", dialog)
}

async function runClearDB() {
  await destroyDB()
  $emit("canSyncFlag", false)
  $q.notify({
    caption: "Локальная БД была очищена, рекомендуется обновить страницу.",
    type: "warning",
  })
}
</script>
