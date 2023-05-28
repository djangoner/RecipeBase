<template>
  <q-btn
    v-if="comments"
    icon="announcement"
    :color="comments[dayIdx] ? 'red' : 'grey'"
    flat
    round
    @click="openComment(dayIdx)"
  >
    <q-tooltip v-if="comments[dayIdx]">
      {{ comments[dayIdx] }}
    </q-tooltip>
  </q-btn>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { WeekDays } from 'src/modules/WeekUtils'
import { computed, PropType } from 'vue'


const props = defineProps({
  dayIdx: {
    type: Number,
    required: true,
  },
  dayStr: {
    type: String,
    default: "",
  },
  modelValue: {
    type: Object as PropType<PlanComments | undefined>,
    required: true,
  },
  canEdit: {
    type: Boolean,
    default: true
  },
})
const $emit = defineEmits(["update-plan", "update:modelValue"])
const $q = useQuasar()


type PlanComments = Record<number, string>

const comments= computed({
  get(){
    return props.modelValue
  },
  set(val: PlanComments | undefined){
    $emit("update:modelValue", val)
  }
})

function openComment(idx: number) {
      if (!comments.value) {
        comments.value = {}
      }

      $q
        .dialog({
          title: `Комментарий - ${props.dayStr}. ${WeekDays[idx]}`,
          // title: "Комментарий",
          prompt: {
            model: comments.value[idx],
            type: "textarea",
            autogrow: true,
            inputStyle: { minHeight: "3rem", maxHeight: "10rem" },
            // readonly: !editMode,
            readonly: !props.canEdit
          },
          cancel: true,
          persistent: true,
        })
        .onOk((comment: string) => {
          if (!props.canEdit) {
            return
          }
          const newComments = Object.assign({}, comments.value)
          newComments[idx] = comment
          comments.value = newComments
          $emit("update-plan")
        })
    }
</script>