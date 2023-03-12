<template>
  <q-select
    :modelValue="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    label="Единица измерения"
    :options="amountTypeList || []"
    :readonly="readonly"
    option-label="title"
    option-value="id"
    map-options
    emit-value
    dense
    options-dense
    clearable
  >
  </q-select>
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
  props: {
    modelValue: {
      type: String as PropType<string | null | AmountTypeEnum>,
      required: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
    };
  },
  mounted() {
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
});
</script>
