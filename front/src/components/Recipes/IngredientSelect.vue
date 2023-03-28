<template>
  <q-select
    :model-value="ingredient"
    :input-debounce="0"
    :options="ingredients"
    :rules="rules"
    :label="label"
    option-label="title"
    use-input
    options-dense
    flat
    dense
    hide-bottom-space
    @update:model-value="$emit('update:ingredient', $event)"
    @filter="filterIngredients"
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
import { IngredientRead } from "src/client"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    ingredient: {
      type: Object as PropType<IngredientRead | undefined>,
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
  },
  emits: ["update:ingredient"],
  data() {
    const store = useBaseStore()
    return { store, search: "", loading: true }
  },
  computed: {
    ingredients() {
      return this.store.ingredients?.filter((v) => v.title.toLowerCase().indexOf(this.search) !== -1).slice(0, 20)
    },
    rules() {
      if (this.required) {
        return [(val: string) => val || "Обязательное поле"]
      }
      return []
    },
  },
  created() {
    if (!this.ingredients || this.store.ingredients_searched) {
      this.loadIngredients()
    }
  },
  methods: {
    filterIngredients(val: string, update: CallableFunction) {
      update(() => {
        this.search = val.toLowerCase()
      })
    },
    loadIngredients() {
      const payload = {
        fields: "id,title",
      }
      this.loading = true
      this.store
        .loadIngredients(payload)
        .then(() => {
          this.loading = false
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки ингредиентов")
        })
    },
  },
})
</script>
