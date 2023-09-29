<template>
  <draggable
    :list="model || []"
    :group="{name: 'plans', pull: dragPull?'clone':false, put: dragPut}"
    item-key="id"
    :animation="200"
    :disable="disable"
    handle=".drag-handle"
    ghost-class="ghost"
    @start="drag = true"
    @end="drag = false"
    @log="log"
  >
    <!-- <template #>
      <transition-group
        type="transition"
        :name="!drag ? 'flip-list' : null"
      /></transition-group>
    </template> -->
    <template #item="{element}">
      <q-item
        dense
      >
        <q-item-section
          avatar
        >
          <div class="row q-gutter-x-sm">
            <q-icon
              name="drag_indicator"
              class="drag-handle cursor-pointer"
              size="sm"
            />
            <q-btn
              v-if="btnAdd"
              icon="add"
              color="positive"
              size="sm"
              dense
              round
              unelevated
              @click="emit('add', element)"
            />
          </div>
        </q-item-section>
        <q-item-section>
          {{ element.title }}
        </q-item-section>
        <q-item-section v-if="btnDel" side>
          <q-btn
            size="sm"
            icon="delete"
            color="negative"
            round
            flat
            @click="removeElement(element)"
          />
        </q-item-section>
      </q-item>
    </template>
  </draggable>
</template>

<script setup lang="ts">
import { useVModel } from '@vueuse/core';
import { RecipeShort } from 'src/client';
import { PropType, ref } from 'vue';
import draggable from 'vuedraggable'

const props = defineProps({
  modelValue: {
    type: Array as PropType<RecipeShort[]>,
    required: true,
  },
  dragPut: {
    type: Boolean,
    default: false,
  },
  dragPull: {
    type: Boolean,
    default: false,
  },
  disable: {
    type: Boolean,
    default: false,
  },
  btnAdd: {
    type: Boolean,
    default: false,
  },
  btnDel: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:model-value', 'add'])

const model = useVModel(props, 'modelValue', emit)
const drag = ref(false)


interface HasId {
  id: number
}

function removeElement(element: HasId){
  model.value = model.value.filter(el => el.id !== element.id)
}

function log(e){
  console.debug(e)
}


</script>

<style lang="scss" scoped>
.ghost {
  opacity: 0.5;
}

</style>