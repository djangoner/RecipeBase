<template>
  <q-select
    :model-value="modelValue"
    :input-debounce="0"
    :options="tags"
    :rules="rules"
    :label="label"
    option-label="title"
    option-value="id"
    use-input
    multiple
    use-chips
    map-options
    emit-value
    options-dense
    dense
    hide-bottom-space
    @update:model-value="$emit('update:model-value', $event)"
    @filter="filterTags"
  >
    <template #no-option>
      <q-item>
        <q-item-section class="text-grey">
          Нет результатов
        </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script lang="ts">
import { useBaseStore } from "src/stores/base"
import { defineComponent, PropType } from "vue"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: {
      type: Object as PropType<number[] | undefined>,
      default: undefined,
      required: false,
    },
    label: {
      type: String,
      default: null,
      required: false,
    },
    required: {
      type: Boolean,
      default: true,
    },
    exclude: {
      type: Array as PropType<number[]>,
      required: false,
      default: () => [],
    },
  },
  emits: ["update:model-value"],
  data() {
    const store = useBaseStore()
    return { store, search: "", loading: true }
  },
  computed: {
    tags() {
      return this.store.tags?.filter((v) => v.title.toLowerCase().indexOf(this.search) !== -1 && this.exclude.indexOf(v.id) === -1).slice(0, 20)
    },
    rules() {
      if (this.required) {
        return [(val: string) => val || "Обязательное поле"]
      }
      return []
    },
  },
  created() {
    if (!this.tags) {
      this.loadTags()
    }
  },
  methods: {
    filterTags(val: string, update: CallableFunction) {
      update(() => {
        this.search = val.toLowerCase()
      })
    },
    loadTags() {
      const payload = {
        fields: "id,title",
      }
      this.loading = true
      this.store
        .loadTags(payload)
        .then(() => {
          this.loading = false
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки меток")
        })
    },
  },
})
</script>
