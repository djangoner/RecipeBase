<template>
  <q-select
    v-bind="$attrs"
    :key="index"
    ref="refSelect"
    popup-content-class="popup__recipe-select"
    :model-value="modelValue"
    :input-debounce="100"
    :options="recipesList || []"
    :readonly="readonly"
    option-label="title"
    use-input
    clearable
    options-dense
    :dense="dense"
    @update:model-value="$emit('update:model-value', $event)"
    @filter="filterRecipes"
    @virtual-scroll="onScroll"
    @popup-show="selectPopup = true"
    @popup-hide="selectPopup = false"
  >
    <template #no-option>
      <q-item>
        <q-item-section class="text-grey">
          Нет результатов
        </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script setup lang="ts">
import { RecipeRead } from "src/client"
import { CustomAxiosError, handleErrors } from "src/modules/HandleErrorsMixin"
import { useBaseStore } from "src/stores/base"
import { PropType, computed, ref, Ref, watch } from "vue"
import {QSelect} from 'quasar'
import { useEventBus } from "@vueuse/core"

const props = defineProps({
  modelValue: {
    type: Object as PropType<RecipeRead>,
    required: false,
    default: undefined,
  },
  dense: {
    type: Boolean,
    default: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  index: {
    type: String,
    default: null,
  },
})

const store = useBaseStore()
const search = ref("")
const loading = ref(false)
const refSelect: Ref<QSelect | null> = ref(null)
const selectPopup = ref(false)

const page = ref(1)
const lastPage = ref(0)
const totalItems = ref(0)
const $emit = defineEmits(["update:model-value"])

const bus = useEventBus<string>('active-recipe-select')

bus.on((event) => {
  if (selectPopup.value && props.index != event){
    refSelect.value?.hidePopup()
  }
})

watch(selectPopup, (val: boolean) => {
  if (val){
    bus.emit(props.index)
  }
})

const recipesList = computed(() => {
  return store.recipes
})

const loadRecipes = () => {
  return new Promise((resolve, reject) => {
    loading.value = true
    const payload = {
      search: search.value,
      fields: "id,title",
      ordering: "-cooked_times",
      pageSize: 20,
      page: page.value,
    }

    store
      .loadRecipes(payload, page.value > 1)
      .then((resp) => {
        loading.value = false
        console.debug("RESP: ", resp)
        if (resp.count) {
          totalItems.value = resp.count
          lastPage.value = Math.ceil(resp.count / payload.pageSize)
        }
        resolve(payload)
      })
      .catch((err: CustomAxiosError) => {
        loading.value = false
        console.warn(err)
        reject(err)
        handleErrors(err, "Ошибка загрузки рецептов")
      })
  })
}
const filterRecipes = (val: string, update: CallableFunction) => {
  if (search.value == val && recipesList.value) {
    update()
    return
  }
  search.value = val
  page.value = 1
  loadRecipes().finally(() => {
    update()
  })
}

const onScroll = ({ index }: { to: number; index: number }) => {
  const lastIndex = (recipesList.value?.length || 1) - 1
  // console.debug("Scroll: ", to, index, lastIndex, page.value, lastPage.value)

  if (loading.value !== true && page.value < lastPage.value && index === lastIndex) {
    // console.debug("Loading more!")
    page.value += 1
    void loadRecipes()
  }
}
</script>

<style lang="scss">
.popup__recipe-select {
  max-height: 400px !important;
}
</style>
