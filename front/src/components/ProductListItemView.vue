<template>
  <q-dialog
    :modelValue="!!modelValue"
    @update:modelValue="$emit('update:modelValue', null)"
    no-route-dismiss
  >
    <q-card style="width: 700px; max-width: 90vw" v-if="item">
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

        <div class="q-my-md row">
          <q-btn
            @click="
              showMoveWeek = true;
              filterWeeks('', () => {});
            "
            v-if="isOnLine"
            label="Перенести на неделю..."
            icon="trending_flat"
            size="sm"
            color="primary"
            dense
          ></q-btn>
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

  <!-- Move to another week dialog -->

  <q-dialog v-model="showMoveWeek" persistent>
    <q-card style="min-width: 350px">
      <q-card-section>
        <div class="text-h6">Перенести задачу на другую неделю</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-select
          label="Неделя для переноса"
          v-model="moveWeek"
          :input-debounce="100"
          :options="weeksList"
          :option-label="(w) => w.year + '.' + w.week"
          @filter="filterWeeks"
          use-input
          clearable
          options-dense
          dense
          autofocus
        />

        <div class="q-mt-md row justify-around">
          <q-btn
            @click="moveWeekDelta(-1)"
            label="Прошлая"
            icon="navigate_before"
            color="primary"
            size="sm"
          />
          <q-btn
            @click="moveWeekDelta(1)"
            label="Следующая"
            icon="navigate_next"
            color="primary"
            size="sm"
          />
        </div>
      </q-card-section>

      <q-card-actions align="right" class="text-primary">
        <q-btn flat label="Отменить" v-close-popup />
        <q-btn @click="itemMoveWeek()" flat label="Перенести" />
      </q-card-actions>
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
    return {
      store,
      WeekDays,
      showMoveWeek: false,
      searchWeek: '',
      moveWeek: null,
      priorityOptions,
    };
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

    filterWeeks(val, update, abort) {
      // if (this.searchWeek == val) {
      //   update(() => {});
      //   return;
      // }
      this.searchWeek = val || '';
      let payload = {
        short: '1',
        search: this.searchWeek.replaceAll('.', ''),
      };

      this.store
        .loadProductListWeeks(payload)
        .then(() => {
          update(() => {});
        })
        .catch(() => {
          update(() => {});
        });
    },
    moveWeekDelta(delta) {
      let year = this.week.year.valueOf();
      let week = this.week.week.valueOf();

      week = week + delta;

      if (week < 0) {
        week = 54;
      } else if (week > 54) {
        week = 1;
      }

      let payload = {
        year: year,
        week: week,
        page_size: 1000,
      };
      this.store.loadProductListWeek(payload, true).then((resp) => {
        this.moveWeek = resp.data;
        delete this.moveWeek['items'];
      });
    },
    itemMoveWeek() {
      if (!this.moveWeek) {
        return;
      }

      let item = Object.assign({}, this.item);

      item.week = this.moveWeek.id;
      this.$emit('updateItem', item, true);
      this.showMoveWeek = false;
      this.$emit('update:modelValue', false);
    },
  },
  computed: {
    item() {
      return this.modelValue || {};
    },
    weeksList() {
      return this.store?.product_lists?.results;
    },
    weekDaysOptions() {
      return Object.entries(this.WeekDays).map(([id, name]) => {
        return { id: parseInt(id), name: name };
      });
    },
  },
  watch: {
    modelValue(val, oldVal) {
      if (val !== oldVal) {
        this.showMoveWeek = false;
      }
    },
  },
};
</script>
