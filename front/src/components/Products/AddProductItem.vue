<template>
  <div class="row items-center q-px-md q-mb-sm">
    <div class="col-grow">
      <select-search
        ref="selectSearchVal"
        behavior="menu"
        label="Добавить продукт"
        dense
        outlined
        use-input
        hide-dropdown-icon
        option-label="title"
        option-value="id"
        options-dense
        :input-debounce="0"
        :options="options"
        @new-value="createItem()"
        @update:model-value="onSelected"
        @filter="filterFn"
      />
    </div>
    <q-btn
      class="col-auto q-ml-md"
      icon="add"
      size="sm"
      color="green"
      dense
      rounded
      unelevated
      @click="createItem()"
    />
  </div>
</template>

<script setup lang="ts">
import { IngredientRead, ProductListItemRead } from "src/client"
import SelectSearch from "src/components/Form/SelectSearch.vue"
import { useBaseStore } from "src/stores/base"
import { computed, ref, Ref, onMounted } from "vue"

const $emit = defineEmits(["create", "select"])

const itemText = ref("")
const selectSearchVal = ref(null)
const options: Ref<ProductListItemRead[] | IngredientRead[]> = ref([])

const store = useBaseStore()

const ingredients = computed(() => store.ingredients)

function loadIngredients(search?: string) {
  const payload = {
    fields: "id,title",
    pageSize: 1000,
    search: search,
  }

  const prom = store.loadIngredients(payload)
  return prom
}

function filterFn(val: string, update: CallableFunction) {
  itemText.value = val
  update(() => {
    const needle = val.toLowerCase()
    if (needle.length < 2) {
      options.value = []
      return
    }
    // options.value = productItems?.value?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1).slice(0, 5) || []
    options.value = ingredients?.value?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1).slice(0, 5) || []
  })
}

function selectClear() {
  if (selectSearchVal.value) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
    selectSearchVal.value?.clear()
  }
}

function onSelected(ing: IngredientRead) {
  console.debug("[ProductItemAdd]Select ", ing)
  $emit("create", ing.title, { ingredient: ing.id })
  itemText.value = ""
  selectClear()
}

function createItem() {
  console.debug("[ProductItemAdd] Create ", itemText.value)
  $emit("create", itemText.value)
  itemText.value = ""
  selectClear()
}

onMounted(() => loadIngredients())
</script>
