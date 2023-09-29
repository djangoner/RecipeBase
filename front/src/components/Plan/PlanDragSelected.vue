<template>
  <plan-gen-drag
    :drag-put="false"
    :drag-pull="true"
    :pull-clone="false"
    @end="onEnd"
    @move="onDrag"
  />
</template>

<script setup lang="ts">
import { useBaseStore } from 'src/stores/base'
import { useLocalStore } from 'src/stores/local'
import PlanGenDrag from './PlanGenDrag.vue'

const store = useBaseStore()
const storeLocal = useLocalStore()

interface DraggedEvent extends Event{
  to: HTMLElement
  dragged?:HTMLElement
  item?:HTMLElement
}

function onDrag(e: DraggedEvent, perform=false){
  const elTo = e.to
  const elItem = (e.dragged || e.item) as HTMLElement

  const dayTo = Number(elTo.dataset.day) || null
  const mealTime = Number(elTo.dataset.mtime) || null
  const recipeId = Number(elItem.dataset.recipe_id) || null
  // const planId = Number(elItem.dataset.plan_id ) || null
  const dragCancell = !dayTo || !mealTime || !recipeId
  console.debug("[Drag] set ", {elTo, elItem, dayTo, mealTime, recipeId, dragCancell})
  if (dragCancell){
    return false
  }

  if (perform){
    const prom = store.setRecipePlan(dayTo, mealTime, recipeId)
    void prom.then((resp) => {
      if (store.week_plan && resp){
        store.week_plan.plans.push(resp)
      }
    })
  }
}

function onEnd(e: DraggedEvent){
  console.debug("[Drag] end", e)
  onDrag(e, true)
  storeLocal.recipesSelectedSave()
}

</script>