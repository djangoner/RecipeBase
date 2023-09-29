<template>
  <plan-recipes-drag
    v-model="recipesSelected"
    :drag-put="true"
    :drag-pull="false"
    btn-del
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useLocalStore } from 'src/stores/local';
import PlanRecipesDrag from './PlanRecipesDrag.vue'


const store = useLocalStore()
const {recipesSelected} = storeToRefs(store)

</script>