<template>
  <div class="row justify-between items-center">
    <q-input
      :model-value="modelValue"
      @update:modelValue="$emit('update:modelValue', $event)"
      :debounce="2000"
      :readonly="readonly"
      class="col-3"
      type="number"
      label="Куплено"
      dense
    />
    <q-slider
      :model-value="modelValue"
      @update:modelValue="$emit('update:modelValue', $event)"
      class="col-grow q-px-md"
      marker-labels
      :debounce="2000"
      :readonly="readonly"
      :min="0"
      :max="max"
      :step="sliderStep"
    ></q-slider>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";

export default defineComponent({
  props: {
    modelValue: {
      type: Number as PropType<number | null>,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    max: {
      type: Number,
      default: 1,
    },
    amount_type: {
      type: String,
      required: false,
    },
  },
  computed: {
    sliderStep(): number {
      if (this.amount_type == "g") {
        return 50;
      }

      return 1;
    },
    markersCount(): number {
      return Math.max(Math.floor(this.max / 10), 1);
    },
  },
});
</script>

<style scoped lang="scss">
:deep(.q-slider) {
  display: flex;
  flex-direction: column;

  .q-slider__track-container {
    padding-top: 5px;
  }

  .q-slider__marker-labels-container {
    order: -1;
    padding-top: 5px;
    padding-bottom: 0;
  }
}
</style>
