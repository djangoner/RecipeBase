<template>
  <q-dialog
    :modelValue="!!modelValue"
    @update:modelValue="$emit('update:modelValue', null)"
  >
    <q-card style="width: 700px; max-width: 90vw">
      <!-- Top row -->
      <q-card-section class="row items-center no-wrap q-pb-none">
        <div class="col row">
          <q-checkbox
            v-model="item.is_completed"
            checked-icon="task_alt"
            unchecked-icon="radio_button_unchecked"
            indeterminate-icon="help"
            size="lg"
            @update:modelValue="$emit('updateItem', item)"
          />
          <div class="row column col">
            <!-- <span class="text-h6 full-width" v-if="item.is_auto">
              {{ item.title }}
            </span> -->
            <q-input
              v-model="item.title"
              @update:modelValue="$emit('updateItem', item)"
              class="col"
              :debounce="500"
              dense
            />

            <span class="text-body2 text-primary">
              <q-icon v-if="item.is_auto" name="settings">
                <q-tooltip>
                  Этот рецепт был создан автоматически на основе плана на неделю
                </q-tooltip>
              </q-icon>
              {{ getDay(item.day) }}
              {{ WeekDays[item.day] }}
            </span>
          </div>
        </div>
        <q-btn class="col-auto" icon="close" flat round dense v-close-popup></q-btn>
      </q-card-section>

      <!-- Content -->
      <q-card-section class="q-pt-none">
        <q-select
          v-if="!item.is_auto"
          v-model.number="item.day"
          @update:modelValue="$emit('updateItem', item)"
          :options="weekDaysOptions"
          label="День недели"
          option-label="name"
          option-value="id"
          map-options
          emit-value
          dense
          options-dense
          use-input
          clearable
        >
        </q-select>
        <q-select
          v-if="!item.is_auto"
          v-model.number="item.priority"
          @update:modelValue="$emit('updateItem', item)"
          :options="priorityOptions"
          label="Приоритет"
          option-label="name"
          option-value="id"
          map-options
          emit-value
          dense
          options-dense
          use-input
        >
        </q-select>

        <!-- Used in recipes -->
        <div class="q-my-md" v-if="item.is_auto && item.ingredients">
          <span class="text-subtitle-1">Используется в рецептах:</span>
          <q-list class="q-my-sm" dense>
            <q-item
              v-for="ing of item.ingredients"
              :key="ing.id"
              clickable
              :to="{ name: 'recipe', params: { id: ing.recipe.id } }"
            >
              {{ ing.recipe.title }} ({{ ingUsingStr(ing) }})
            </q-item>
          </q-list>
        </div>

        <!-- Ingredient description -->
        <q-input
          v-model="item.description"
          @update:modelValue="$emit('updateItem', item)"
          :debounce="1000"
          type="textarea"
          label="Описание"
        />
      </q-card-section>

      <!-- Botom actions -->
      <!-- <q-card-actions align="center">
        <q-btn flat label="OK" color="primary" v-close-popup />
      </q-card-actions> -->
    </q-card>
  </q-dialog>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import { getDateOfISOWeek, WeekDays, getWeekNumber } from 'components/WeekSelect.vue';
import { date } from 'quasar';

let priorityOptions = [
  {
    id: 1,
    name: 'Наивысший',
  },
  {
    id: 2,
    name: 'Высокий',
  },
  {
    id: 3,
    name: 'Средний',
  },
  {
    id: 4,
    name: 'Низкий',
  },
  {
    id: 5,
    name: 'Низший',
  },
];

export default {
  props: { modelValue: { required: true }, week: {} },
  emits: ['openItem', 'updateItem', 'update:modelValue'],
  data() {
    const store = useBaseStore();
    return { store, WeekDays, priorityOptions };
  },
  methods: {
    getDay(idx) {
      let fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, 'DD.MM');
    },
    ingUsingStr(ing) {
      let recipe = ing.recipe;

      let ings = recipe.ingredients.filter((i) => i.id == ing.id);
      let texts = ings.map((i) => {
        let r = i.amount + ' ' + i.amount_type_str;
        if (i.is_main) {
          r += ', основной';
        }
        return r;
      });

      return texts.join(', ');
    },
  },
  computed: {
    item() {
      return this.modelValue;
    },
    weekDaysOptions() {
      return Object.entries(this.WeekDays).map(([id, name]) => {
        return { id: parseInt(id), name: name };
      });
    },
  },
};
</script>
