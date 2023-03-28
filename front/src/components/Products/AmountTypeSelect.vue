<template>
  <q-select
    :model-value="modelValue"
    :label="label || undefined"
    :options="amountTypeList || []"
    :readonly="readonly"
    option-label="title"
    option-value="id"
    map-options
    emit-value
    dense
    options-dense
    clearable
    @update:model-value="$emit('update:model-value', $event)"
  />
</template>

<script lang="ts">
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import { useBaseStore } from "src/stores/base";
import { defineComponent, PropType } from "vue";
import { AmountTypesConvert, AmountTypesTypes } from "src/modules/Globals";
import { AmountTypeEnum } from "src/client";

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: {
      type: String as PropType<string | null | AmountTypeEnum>,
      required: true,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String as PropType<string | null>,
      default: "Единица измерения",
    }
  },
  emits: ['update:model-value'],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
    };
  },
  computed: {
    amount_types() {
      return this.store.amount_types;
    },
    amountTypeList() {
      return this.amount_types?.types as AmountTypesTypes;
    },
    amountTypeConvert() {
      return this.amount_types?.convert as AmountTypesConvert;
    },
  },
  created() {
    if (!this.amount_types) {
      this.loadAmountTypes();
    }
  },
  methods: {
    loadAmountTypes() {
      this.loading = true;
      this.store
        .loadAmountTypes()
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка загрузки типов измерений");
        });
    },
  },
});
</script>
