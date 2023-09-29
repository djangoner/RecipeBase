<template>
  <q-tabs
    v-model="tab"
    animated
    dense
    no-caps
  >
    <q-tab
      label="Недавние"
      name="recent"
    />
    <q-tab
      label="Популярные"
      name="popular"
    />
  </q-tabs>

  <q-scroll-area style="height: 560px;">
    <q-linear-progress
      :indeterminate="isLoading"
      instant-feedback
      color="primary"
    />
    <plan-recipes-drag
      :model-value="recipesFiltered"
      :drag-pull="true"
      btn-add
      v-bind="$attrs"
      @add="emit('add', $event)"
    />
  </q-scroll-area>
</template>

<script setup lang="ts">
import { useLocalStorage } from '@vueuse/core';
import { RecipeShort } from 'src/client';
import { promiseSetLoading } from 'src/modules/StoreCrud';
import { useBaseStore } from 'src/stores/base';
import { computed, onMounted, PropType, Ref, ref, watch } from 'vue';
import PlanRecipesDrag from './PlanRecipesDrag.vue'

const props = defineProps({
  exclude: {
    type: Array as PropType<number[]>,
    default: null,
  }
})

const emit = defineEmits(['add'])

const store = useBaseStore()
// const {recipes} = storeToRefs(store)
const recipes: Ref<RecipeShort[]> = ref([])

const tab = useLocalStorage("planGenTab", "recent")
const isLoading = ref(false)

const recipesFiltered = computed(() => {
  let res = recipes.value
  if (props.exclude && res){
    res = res.filter(el => props.exclude.indexOf(el.id) === -1)
  }
  return res
})

// function load(){
//   void store.loadRecipes({})
// }

function getPayload(){
  const result = {
    pageSize: 20,
    fields: 'id,title',
    compilation: "",
    ordering: "-last_cooked",
  }

  switch (tab.value) {
    case "recent":
      result.compilation = "recent"
      result.ordering = "-last_cooked"
      break;
      case "popular":
        result.compilation = "top10"
        result.ordering = "-cooked_times"
      break;

    default:
      break;
  }

  return result
}

function loadRecipes(){
  const payload = getPayload()
  const prom = store.loadRecipes(payload, false)

  promiseSetLoading(prom, isLoading)
  void prom.then((resp) => {
    recipes.value = resp.results as RecipeShort[]
  })
}

onMounted(() => {
  loadRecipes()
})

watch(tab, loadRecipes)

</script>