<template>
  <q-select
    :model-value="ingredient"
    :input-debounce="preloadAll ? 0 : 100"
    :options="ingredients"
    :rules="rules"
    :label="label"
    :readonly="readonly"
    :disable="disable"
    :clearable="clearable"
    option-label="title"
    use-input
    options-dense
    flat
    dense
    hide-bottom-space
    @update:model-value="$emit('update:ingredient', $event)"
    @filter="filterIngredients"
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

<script lang="ts" setup>
import { useBaseStore } from "src/stores/base"
import { computed, PropType, ref } from "vue"
import { IngredientRead } from "src/client"
import { promiseSetLoading } from "src/modules/StoreCrud"

const props = defineProps({
  ingredient: {
    type: Object as PropType<IngredientRead | undefined>,
    default: undefined,
    required: false,
  },
  label: {
    type: String,
    default: null,
    required: false,
  },
  required: {
    type: Boolean,
    default: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  disable: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  preloadAll: {
    type: Boolean,
    default: true,
  },
})
const $emit = defineEmits(["update:ingredient"])
const store = useBaseStore()
const search = ref("")
const loading = ref(false)

const ingredients = computed(() => {
  return store.ingredients?.filter((v) => v.title.toLowerCase().indexOf(search.value) !== -1).slice(0, 20)
})
const rules = computed(() => {
  if (props.required) {
    return [(val: string) => val || "Обязательное поле"]
  }
  return []
})


function filterIngredients(val: string, update: CallableFunction) {
  update(() => {
    if (props.preloadAll) {
      if (!ingredients.value || store.ingredients_searched) {
        loadIngredients()
      }
      search.value = val.toLowerCase()

    } else {
      loadIngredients(val)
    }
  })
}
const loadIngredients = (search?: string) => {
  const payload = {
    fields: "id,title,type",
    pageSize: 1000,
    search: search,
  }
  if (!props.preloadAll) {
    payload.pageSize = 20
  }

  const prom = store.loadIngredients(payload)
  promiseSetLoading(prom, loading)

  loading.value = true
}


// onMounted(() => {
//   if (!ingredients.value || store.ingredients_searched) {
//     loadIngredients()
//   }
// })
</script>
