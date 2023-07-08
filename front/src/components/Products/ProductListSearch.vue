<template>
  <q-btn
    icon="search"
    size="sm"
    dense
    rounded
    flat
  >
    <q-popup-proxy>
      <q-card>
        <q-card-section>
          <q-select
            label="Поиск"
            autofocus
            use-input
            option-label="title"
            option-value="id"
            :options-dense="$q.screen.gt.sm"
            :input-debounce="0"
            :options="options"
            outlined
            behavior="menu"
            @update:model-value="onSelected"
            @filter="filterFn"
          />
        </q-card-section>
      </q-card>
    </q-popup-proxy>
  </q-btn>
</template>

<script setup lang="ts">
import { ProductListItemRead } from 'src/client';
import { useBaseStore } from 'src/stores/base';
import { computed, ref, Ref } from 'vue';


const $emit = defineEmits(["select"])

const store = useBaseStore()

const options: Ref<ProductListItemRead[]> = ref([])

const productItems = computed(() => store.product_list?.items)

function filterFn(val: string, update: CallableFunction) {
  update(() => {
    const needle = val.toLowerCase()
    if (needle.length < 1) {
      options.value = []
      return
    }
    options.value = productItems?.value?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1).slice(0, 5) || []
  })
}

function onSelected(productItem: ProductListItemRead) {
  console.debug("[ProductItemAdd]Select ", productItem)
  $emit("select", productItem)
}

</script>