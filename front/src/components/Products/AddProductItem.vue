<template>
  <div class="row items-center q-px-md q-mb-sm">
    <div class="col-grow">
      <select-search
        ref="selectSearch"
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
import { ProductListItemRead } from "src/client"
import SelectSearch from "src/components/Form/SelectSearch.vue"
import { useBaseStore } from "src/stores/base"
import { computed, ref, Ref } from "vue"

const $emit = defineEmits(["create", "select"])

const itemText = ref("")
const selectSearch = ref(null)
const options: Ref<ProductListItemRead[]> = ref([])

const store = useBaseStore()

const productItems = computed(() => store.product_list?.items)


function filterFn(val: string, update: CallableFunction) {
  itemText.value = val
  update(() => {
    const needle = val.toLowerCase()
    if (needle.length < 2){
      options.value = []
      return
    }
    options.value = productItems?.value?.filter(v => v.title.toLowerCase().indexOf(needle) > -1).slice(0, 5) || []
  })
}

function onSelected(productItem: ProductListItemRead){
  console.debug("[ProductItemAdd]Select ", productItem)
  $emit("select", productItem)
  itemText.value = ""
  if (selectSearch.value){
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
    selectSearch.value?.clear()
  }
}

function createItem() {
  console.debug("[ProductItemAdd] Create ", itemText.value)
  $emit("create", itemText.value)
  itemText.value = ""
}
</script>
