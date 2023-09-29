<template>
  <q-dialog
    v-model="showModal"
    v-bind="$attrs"
  >
    <q-card
      style="width: 700px; max-width: 80vw"
      :style="cardStyle"
    >
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">
          {{ title }}
        </div>
        <q-space />
        <q-btn
          v-close-popup
          icon="close"
          flat
          round
          dense
        />
      </q-card-section>

      <slot name="before" />

      <q-card-section>
        <slot name="default" />
      </q-card-section>

      <slot name="after" />
      <slot name="actions" />
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useVModel } from "@vueuse/core"

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  cardStyle: {
    type: [String, Array],
    default: "",
  },
  title: {
    type: String,
    default: "",
  },
})

const emit = defineEmits(["update:model-value"])

const showModal = useVModel(props, "modelValue", emit)
</script>
