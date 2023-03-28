<template>
  <q-form
    @submit="$emit('submit', $event)"
    @reset="$emit('reset', $event)"
  >
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Время готовки
      </h6>
      <q-range
        v-model="filters.cooking_time"
        class="q-px-md"
        :min="5"
        :max="120"
        :step="5"
        label
      />
    </div>

    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Метки
      </h6>
      <tags-select
        v-model="filters.tags_include"
        :exclude="filters.tags_exclude"
        label="Включить"
      />
      <tags-select
        v-model="filters.tags_exclude"
        :exclude="filters.tags_include"
        label="Исключить"
      />
    </div>
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Ингредиенты
      </h6>
      <ingredients-select
        v-model="filters.ingredients_include"
        :exclude="filters.ingredients_exclude"
        label="Включить"
      />
      <ingredients-select
        v-model="filters.ingredients_exclude"
        :exclude="filters.ingredients_include"
        label="Исключить"
      />
    </div>
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Рейтинг
      </h6>
    </div>

    <div class="q-my-sm">
      <search-rating v-model="filters" />

      <div class="row justify-around">
        <q-btn
          type="reset"
          color="negative"
          size="sm"
          icon="close"
        >
          Сбросить
        </q-btn>
        <q-btn
          type="submit"
          color="primary"
          size="sm"
          icon="search"
        >
          Поиск
        </q-btn>
      </div>
    </div>
  </q-form>
</template>

<script lang="ts">
import SearchRating from './SearchRating.vue'
import TagsSelect from './TagsSelect.vue'
import IngredientsSelect from './IngredientsSelect.vue'

import { defineComponent, PropType } from 'vue';
import { RecipesFilters } from 'src/modules/Globals';


export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { IngredientsSelect, TagsSelect, SearchRating },
  props: {
    modelValue: {
      type: Object as PropType<RecipesFilters>,
        required: true,
    },
  },
  emits: ["update:model-value", "submit", "reset"],
  data(){
    return {}
  },
  computed: {
    filters: {
      get(){
        return this.modelValue
      },
      set(val: RecipesFilters){
        this.$emit("update:model-value", val)
      }
    },
  },
  methods: {

  }
})
</script>