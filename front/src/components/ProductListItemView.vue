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
              :readonly="item.is_auto"
              dense
            />

            <span class="text-body2 text-primary">
              <q-icon v-if="item.is_auto" name="settings">
                <q-tooltip>
                  Этот рецепт был создан автоматически на основе плана на неделю
                </q-tooltip>
              </q-icon>
              {{ item.day ? getDay(item.day) : '' }}
              {{ item.day ? WeekDays[item.day] : '' }}
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
          v-model="item.ingredient"
          @update:modelValue="$emit('updateItem', item)"
          label="Ингредиент"
          @filter="filterIngredients"
          :options="ingredients || []"
          :readonly="item.is_auto"
          option-label="title"
          option-value="id"
          map-options
          dense
          options-dense
          use-input
          clearable
        >
        </q-select>
        <q-select
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
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey"> Нет результатов </q-item-section>
            </q-item>
          </template>
        </q-select>

        <!-- Used in recipes -->
        <div class="q-my-md" v-if="item.is_auto && item.ingredients">
          <span class="text-subtitle-1">Используется в рецептах:</span>
          <q-list class="q-my-sm" dense>
            <q-item
              class="items-center"
              v-for="ing of item.ingredients"
              :key="ing.id"
              clickable
              :to="{ name: 'recipe', params: { id: ing.recipe.id } }"
            >
              <small class="ing-day"
                >{{ getRecipeDays(ing.recipe)?.join(',') }}.&nbsp;</small
              >
              {{ ing.recipe.title }} ({{ ingUsingStr(ing) }})
            </q-item>

            <template v-if="item.ingredient.regular_ingredients">
              <q-separator />
              <q-item
                class="items-center q-mt-xs"
                items_center
                clickable
                :to="{
                  name: 'recipe',
                  params: { id: item.ingredient.regular_ingredients.id },
                }"
              >
                <small class="ing-day">-.&nbsp;</small>
                Регулярный ({{ item.ingredient.regular_ingredients.amount }}
                {{ item.ingredient.regular_ingredients.amount_type_str }})
              </q-item>
            </template>
          </q-list>
          <template v-if="item.price_full">
            <div>Цена {{ item.price_full }}₺ (~{{ item.price_part }}₺ необходимо)</div>
          </template>
        </div>

        <div class="q-my-md q-col-gutter-x-md row">
          <div>
            <q-btn
              @click="
                showMoveWeek = true;
                filterWeeks('', () => {});
              "
              v-if="isOnLine"
              label="Перенести на неделю..."
              icon="swap_horiz"
              size="sm"
              color="primary"
              no-caps
              dense
            ></q-btn>
          </div>
          <div>
            <q-btn
              v-if="isOnLine && item?.ingredient"
              :to="{ name: 'ingredient', params: { id: item?.ingredient?.id } }"
              label="Открыть ингредиент"
              icon="open_in_new"
              size="sm"
              color="primary"
              no-caps
              dense
            ></q-btn>
          </div>
        </div>

        <!-- Product list ingredient description -->
        <q-input
          v-model="item.description"
          @update:modelValue="$emit('updateItem', item)"
          :debounce="1000"
          type="textarea"
          label="Описание"
          autogrow
          input-style="max-height: 5rem;"
        />

        <!-- Ingredient description -->
        <q-input
          v-if="item.ingredient"
          :modelValue="item?.ingredient?.description"
          :debounce="1000"
          type="textarea"
          label="Описание ингредиента"
          autogrow
          readonly
        />
      </q-card-section>

      <!-- Bottom actions -->
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
          :options="weeksList || []"
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

<script lang="ts">
import { useBaseStore } from 'src/stores/base';
import {
  getDateOfISOWeek,
  WeekDays,
  WeekDaysShort,
  YearWeek,
} from 'src/modules/WeekUtils';
import { date } from 'quasar';
import { defineComponent, PropType } from 'vue';
import { priorityOptions } from 'src/modules/Globals';
import {
  ProductListItemRead,
  ProductListWeekRead,
  RecipeIngredientWithRecipeRead,
  RecipeRead,
  RecipeShort,
} from 'src/client';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import IsOnlineMixin from 'src/modules/IsOnlineMixin';

interface ProductListItemAmount {
  amount: number;
  amount_type: string;
  amount_type_str: string;
  amount_grams: number;
  is_main: boolean;
}

interface ProductListItemAmounts {
  [id: number]: ProductListItemAmount[];
}

export default defineComponent({
  props: {
    modelValue: { required: false, type: Object as PropType<ProductListItemRead> },
    week: { required: true, type: Object as PropType<YearWeek> },
  },
  emits: ['openItem', 'updateItem', 'update:modelValue'],
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      WeekDays,
      showMoveWeek: false,
      searchWeek: '',
      moveWeek: null as null | ProductListWeekRead,
      priorityOptions,
    };
  },
  methods: {
    getDay(idx: number): string {
      let fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, 'DD.MM');
    },
    ingUsingStr(ing: RecipeIngredientWithRecipeRead): string {
      let recipe = ing.recipe;
      if (!recipe) {
        return '';
      }

      const amounts = this.item?.amounts as ProductListItemAmounts;
      const ings = amounts[recipe.id] || [];

      const texts = ings.map((i) => {
        let r = String(i.amount) + ' ' + i.amount_type_str;
        if (i.is_main) {
          r += ', основной';
        }
        return r;
      });
      return texts.join(', ');
    },

    filterWeeks(val: string, update: CallableFunction) {
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
          update();
        })
        .catch(() => {
          update();
        });
    },
    loadIngredients(search: string): Promise<void> {
      return new Promise((resolve, reject) => {
        let payload = {
          page_size: 1000,
          search: search,
        };
        this.store
          .loadIngredients(payload)
          .then(() => {
            resolve();
            // this.loading = false;
          })
          .catch((err: CustomAxiosError) => {
            reject(err);
            // this.loading = false;
            this.handleErrors(err, 'Ошибка загрузки ингредиентов');
          });
      });
    },
    filterIngredients(val: string, update: CallableFunction) {
      void this.loadIngredients(val).then(() => {
        void update();
      });
    },
    moveWeekDelta(delta: number) {
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
      void this.store.loadProductListWeek(payload, true).then((resp) => {
        this.moveWeek = resp;
        // delete this.moveWeek['items'];
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
    getRecipeDays(recipe: RecipeRead | RecipeShort): null | string[] {
      if (!this.plan) {
        return null;
      }
      let plans = this.plan.plans.filter((p) => p.recipe.id == recipe?.id);
      return plans.map((p) => (p.day ? WeekDaysShort[p.day] : ('' as string)));
    },
  },
  computed: {
    item() {
      return this.modelValue;
    },
    plan() {
      return this.store.week_plan;
    },
    ingredients() {
      return this.store.ingredients;
    },
    weeksList() {
      return Object.freeze(this.store?.product_lists);
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
});
</script>

<style lang="scss">
.ing-day {
  min-width: 20px;
}
</style>
