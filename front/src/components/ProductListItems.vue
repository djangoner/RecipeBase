<template>
  <q-item
    class="cursor-pointer non-selectable"
    :class="[item.is_completed ? 'bg-grey-4' : '']"
    v-for="item of listItems"
    :key="item.id"
    @click="$emit('openItem', item)"
    clickable
  >
    <!-- Checkbox -->
    <q-checkbox
      v-model="item.is_completed"
      checked-icon="task_alt"
      unchecked-icon="radio_button_unchecked"
      size="lg"
      @update:modelValue="$emit('updateItem', item)"
    />

    <!-- First column -->
    <div class="row column">
      <span class="text-subtitile2">
        <!-- Product title -->
        {{ item.title }}

        <!-- Product amount -->
        <template v-if="item.amount">
          (
          <template v-if="item.ingredient.min_pack_size">
            ~{{ Math.ceil(item.amount / item.ingredient.min_pack_size) }}
            шт.,
          </template>
          {{ item.amount }} {{ item.amount_type_str }}
          )
        </template>
      </span>
      <!-- First column bottom row, date -->
      <span class="text-body2" :class="WeekDaysColors[item.day]">
        <q-icon v-if="item.is_auto" name="settings">
          <q-tooltip>
            Этот рецепт был создан автоматически на основе плана на неделю
          </q-tooltip>
        </q-icon>
        <q-icon v-else name="edit"></q-icon>

        <q-badge class="q-mx-sm q-py-xs" :color="priorityColors[item.priority]">
          <q-icon name="flag" size="10px" />
          <span class="q-ml-xs">
            {{ item.priority }}
          </span>
        </q-badge>
        <q-icon name="notes" size="17px" color="blue-grey" v-if="item.description" />

        {{ getDay(item.day) }}
        {{ WeekDays[item.day] }}
      </span>
    </div>
  </q-item>
</template>

<script>
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
} from 'components/WeekSelect.vue';
import { date } from 'quasar';

let WeekDaysColors = {
  0: 'text-light-green-6',
  1: 'text-teal',
  2: 'text-cyan',
  3: 'text-light-blue',
  4: 'text-blue-10',
  5: 'text-indigo',
  6: 'text-purple',
  7: 'text-deep-purple',
};

let priorityColors = {
  1: 'red',
  2: 'orange',
  3: 'yellpw',
  4: 'green',
  5: 'grey',
};

export default {
  props: { modelValue: { required: true }, week: {} },
  emits: ['openItem', 'updateItem', 'update:modelValue'],

  data() {
    return {
      listItems: null,
      WeekDays,
      WeekDaysColors,
      priorityColors,
    };
  },
  methods: {
    getDay(idx) {
      let fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, 'DD.MM');
    },
    intFormat(number, val1, val2, val3) {
      let n = number.toString();
      if (n > 10 && n < 20) {
        return val3;
      } else if (n.endsWith('1')) {
        return val1;
      } else if (n.endsWith('2') || n.endsWith('3') || n.endsWith('4')) {
        return val2;
      } else {
        return val3;
      }
      return number;
    },
  },
  computed: {},
  watch: {
    listItems(val, oldVal) {
      if (val == oldVal) {
        return;
      }
      this.$emit('update:modelValue', val);
    },
    modelValue(val, oldVal) {
      if (val == oldVal) {
        return;
      }
      this.listItems = val;
    },
  },
};
</script>
