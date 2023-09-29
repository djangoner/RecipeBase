<template>
  <draggable
    :list="model || []"
    :group="{name: 'plans', pull: pullValue, put: dragPut}"
    item-key="id"
    :sort="true"
    :animation="200"
    :disable="disable"
    filter=".not-draggable"
    handle=".drag-handle"
    ghost-class="ghost"
    v-bind="$attrs"
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
        :data-recipe_id="element.id"
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
              class="ghost-hide"
              icon="add_circle"
              color="positive"
              size="sm"
              dense
              round
              flat
              @click="emit('add', element)"
            />
          </div>
        </q-item-section>
        <q-item-section>
          {{ element.title }}
        </q-item-section>
        <q-item-section
          v-if="btnDel"
          side
        >
          <q-btn
            class="ghost-hide"
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
import { computed, PropType, ref } from 'vue';
import draggable from 'vuedraggable'

const props = defineProps({
  modelValue: {
    type: Array as PropType<RecipeShort[]>,
    required: true,
  },
  dragPut: { // Can be elements inserted into this
    type: Boolean,
    default: false,
  },
  dragPull: { // Can be these elements dragged into another
    type: Boolean,
    default: false,
  },
  pullClone: {
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

const pullValue = computed(() => {
  if (props.dragPull){
    return props.pullClone ? 'clone' : true
  }
  return false
})

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

  .ghost-hide {
    display: none!important;
  }
}

</style>