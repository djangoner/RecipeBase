<template>
  <q-select
    :model-value="modelValue"
    :input-debounce="100"
    :options="recipesList || []"
    :readonly="readonly"
    option-label="title"
    use-input
    clearable
    options-dense
    dense
    @update:model-value="$emit('update:model-value', $event)"
    popup-content-style="height: 400px"
    @filter="filterRecipes"
    @virtual-scroll="onScroll"
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
import { PropType, computed, ref } from "vue"

const props = defineProps({
  modelValue: {
    type: Object as PropType<RecipeRead>,
    required: false,
    default: undefined,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
})
const store = useBaseStore()
const search = ref("")
const loading = ref(false)

const page = ref(1)
const lastPage = ref(0)
const totalItems = ref(0)
const $emit = defineEmits(["update:model-value"])

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
  loadRecipes().finally(() => {
    page.value = 1
    update()
  })
}

const onScroll = ({ to, index }: { to: number, index: number }) => {
  const lastIndex = (recipesList.value?.length || 1) - 1
  console.debug("Scroll: ", to, index, lastIndex, page.value, lastPage.value)

  if (loading.value !== true && page.value < lastPage.value && index === lastIndex) {
    console.debug("Loading more!")
    page.value += 1
    void loadRecipes()
  }
}

</script>
