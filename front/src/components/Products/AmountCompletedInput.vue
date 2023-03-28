<template>
  <div class="row justify-between items-center">
    <q-input
      :model-value="modelValue"
      :debounce="2000"
      :readonly="readonly"
      class="col-3"
      type="number"
      label="Куплено"
      dense
      @update:model-value="$emit('update:model-value', $event)"
    />
    <q-slider
      :model-value="modelValue || 0"
      class="col-grow q-px-md"
      marker-labels
      :readonly="readonly"
      :min="0"
      :max="max"
      :step="sliderStep"
      @update:model-value="debouncedUpdate"
    />
  </div>
</template>

<script lang="ts">
import { debounce } from "quasar";
import { defineComponent, PropType } from "vue";

export default defineComponent({
  props: {
    modelValue: {
      type: Number as PropType<number | null>,
        required: true,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    max: {
      type: Number,
      default: 1,
    },
    amountType: {
      type: String,
      default: undefined,
      required: false,
    },
  },
  emits:['update:model-value'],
  data() {
    // eslint-disable-next-line @typescript-eslint/no-empty-function, @typescript-eslint/no-unused-vars
    const emptyFn = ($ev: number | null) => {};
    return { debouncedUpdate: emptyFn as (value: number | null) => void };
  },
  computed: {
    sliderStep(): number {
      // if (this.amountType == "g") {
      //   return 50;
      // }

      return 1;
    },
    markersCount(): number {
      if (this.max < 1000) {
        return Math.max(Math.floor(this.max / 10), 1);
      } else {
        return Math.max(Math.floor(this.max / 5), 1);
      }
    },
  },
  created() {
    this.debouncedUpdate = debounce(
      ($ev) => this.$emit("update:model-value", $ev),
      1000
    );
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
