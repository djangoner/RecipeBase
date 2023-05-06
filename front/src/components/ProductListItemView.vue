<template>
  <q-dialog
    :model-value="!!modelValue"
    no-route-dismiss
    @update:model-value="$emit('update:model-value', null)"
  >
    <q-card
      v-if="item"
      style="width: 700px; max-width: 90vw"
    >
      <!-- Top row -->
      <q-card-section class="row items-center no-wrap q-pb-none">
        <div class="col row">
          <q-checkbox
            v-model="item.is_completed"
            :color="item.already_completed?'info':'primary'"
            checked-icon="task_alt"
            unchecked-icon="radio_button_unchecked"
            indeterminate-icon="help"
            size="lg"
            :disable="!canEdit"
            @update:model-value="$emit('updateItem', item)"
          />
          <div class="row column col">
            <!-- <span class="text-h6 full-width" v-if="item.is_auto">
              {{ item.title }}
            </span> -->
            <q-input
              v-model="item.title"
              class="col"
              :debounce="500"
              :readonly="item.is_auto || !canEdit"
              dense
              @update:model-value="$emit('updateItem', item)"
            />

            <span class="text-body2 text-primary">
              <q-icon
                v-if="item.is_auto"
                name="settings"
              >
                <q-tooltip>
                  Этот рецепт был создан автоматически на основе плана на неделю
                </q-tooltip>
              </q-icon>
              <!-- <template v-if="item && item.day">{{ item || item.day === 0 ? getDay(item.day) : "" }}</template> -->
              {{ item.day || item.day === 0 ? WeekDays[item.day] : "" }}
            </span>
          </div>
        </div>
        <q-btn
          v-close-popup
          class="col-auto"
          icon="close"
          flat
          round
          dense
        />
      </q-card-section>

      <!-- Content -->
      <q-card-section class="q-pt-none">
        <q-select
          v-if="!item.is_auto"
          v-model.number="item.day"
          :options="weekDaysOptions"
          :readonly="item.is_auto || !canEdit"
          label="День недели"
          option-label="name"
          option-value="id"
          map-options
          emit-value
          dense
          options-dense
          use-input
          clearable
          @update:model-value="$emit('updateItem', item)"
        />
        <q-select
          v-model="item.ingredient"
          label="Ингредиент"
          :debounce="100"
          :options="ingredients || []"
          :readonly="item.is_auto || !canEdit"
          :input-debounce="100"
          option-label="title"
          option-value="id"
          map-options
          dense
          options-dense
          use-input
          clearable
          @update:model-value="$emit('updateItem', item)"
          @filter="filterIngredients"
        />

        <q-expansion-item
          label="Дополнительно"
          dense
        >
          <q-toggle
            v-model="item.already_completed"
            label="Уже есть"
            @update:model-value="$emit('updateItem', item)"
          >
            <q-tooltip>
              Продукт уже есть и его не требуется покупать
            </q-tooltip>
          </q-toggle>
          <q-select
            v-model.number="item.priority"
            :options="priorityOptions"
            :readonly="!canEdit"
            label="Приоритет"
            option-label="name"
            option-value="id"
            map-options
            emit-value
            dense
            options-dense
            @update:model-value="$emit('updateItem', item)"
          >
            <template #no-option>
              <q-item>
                <q-item-section class="text-grey">
                  Нет результатов
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <!-- Manual amount -->
          <div
            v-if="!item.is_auto"
            class="row justify-between items-center"
          >
            <q-input
              v-model.number="item.amount"
              :debounce="2000"
              class="col-3"
              type="number"
              label="Количество"
              dense
              @update:model-value="$emit('updateItem', item)"
            />
            <amount-type-select
              v-model="item.amount_type"
              :readonly="!canEdit"
              class="col-grow"
              @update:model-value="$emit('updateItem', item)"
            />
          </div>

          <!-- Completed amount -->

          <amount-completed-input
            v-if="item?.amount"
            v-model.number="item.amount_completed"
            :max="Math.ceil(item.packs) || item.amount || 1"
            :readonly="!canEdit"
            :amount-type="item.amount_type || ''"
            @update:model-value="$emit('updateItem', item)"
          />
        </q-expansion-item>

        <!-- Used in recipes -->
        <div
          v-if="item.is_auto && item.ingredients"
          class="q-my-md"
        >
          <span class="text-subtitle-1">Используется в рецептах:</span>
          <q-list
            class="q-my-sm"
            dense
          >
            <q-item
              v-for="ing of item.ingredients"
              :key="ing.id"
              class="items-center"
              clickable
              :to="{ name: 'recipe', params: { id: ing.recipe.id } }"
            >
              <small class="ing-day">{{ getRecipeDays(ing.recipe)?.join(",") }}.&nbsp;</small>
              {{ ing.recipe.title }} ({{ ingUsingStr(ing) }})
            </q-item>

            <template v-if="item.ingredient && item.ingredient.regular_ingredients">
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
            <div>
              Цена {{ item.price_full }}₺ (~{{ item.price_part }}₺ необходимо)
            </div>
          </template>
        </div>

        <div class="q-my-md q-col-gutter-x-md row">
          <div>
            <q-btn
              v-if="isOnLine && canEdit"
              label="Перенести на неделю..."
              icon="swap_horiz"
              size="sm"
              color="primary"
              no-caps
              dense
              @click="
                showMoveWeek = true;
                filterWeeks('', () => {});
              "
            />
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
            />
          </div>
        </div>

        <!-- Product list ingredient description -->
        <q-input
          v-model="item.description"
          :debounce="1000"
          :readonly="!canEdit"
          type="textarea"
          label="Описание"
          autogrow
          input-style="max-height: 5rem;"
          @update:model-value="$emit('updateItem', item)"
        />

        <!-- Ingredient description -->
        <q-input
          v-if="item?.ingredient"
          :model-value="item?.ingredient?.description"
          :debounce="1000"
          type="textarea"
          label="Описание ингредиента"
          autogrow
          readonly
        />

        <div
          v-if="item?.ingredient?.image"
          class="q-mt-md"
        >
          <div class="text-subtitle1 text-grey q-mb-sm">
            Изображение рецепта
          </div>
          <q-img
            :src="item.ingredient.image"
            fit="contain"
          />
        </div>
      </q-card-section>

      <!-- Bottom actions -->
      <!-- <q-card-actions align="center">
        <q-btn flat label="OK" color="primary" v-close-popup />
      </q-card-actions> -->
    </q-card>
  </q-dialog>

  <!-- Move to another week dialog -->

  <q-dialog
    v-model="showMoveWeek"
    persistent
  >
    <q-card style="min-width: 350px">
      <q-card-section>
        <div class="text-h6">
          Перенести задачу на другую неделю
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-select
          v-model="moveWeek"
          label="Неделя для переноса"
          :input-debounce="100"
          :options="weeksList || []"
          :option-label="(w) => w.year + '.' + w.week"
          use-input
          clearable
          options-dense
          dense
          autofocus
          @filter="filterWeeks"
        />

        <div class="q-mt-md row justify-around">
          <q-btn
            label="Прошлая"
            icon="navigate_before"
            color="primary"
            size="sm"
            @click="moveWeekDelta(-1)"
          />
          <q-btn
            label="Следующая"
            icon="navigate_next"
            color="primary"
            size="sm"
            @click="moveWeekDelta(1)"
          />
        </div>
      </q-card-section>

      <q-card-actions
        align="right"
        class="text-primary"
      >
        <q-btn
          v-close-popup
          flat
          label="Отменить"
        />
        <q-btn
          flat
          label="Перенести"
          @click="itemMoveWeek()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script lang="ts">
import { useBaseStore } from "src/stores/base";
import {
  getDateOfISOWeek,
  WeekDays,
  WeekDaysShort,
  YearWeek,
} from "src/modules/WeekUtils";
import { date } from "quasar";
import { defineComponent, PropType } from "vue";
import { priorityOptions } from "src/modules/Globals";
import {
  ProductListItemRead,
  ProductListWeekRead,
  RecipeIngredientWithRecipeRead,
  RecipeRead,
  RecipeShort,
} from "src/client";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import IsOnlineMixin from "src/modules/IsOnlineMixin";
import AmountTypeSelect from "./Products/AmountTypeSelect.vue";
import AmountCompletedInput from "./Products/AmountCompletedInput.vue";

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
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { AmountTypeSelect, AmountCompletedInput },
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  props: {
    modelValue: {
      required: false,
      default: undefined,
      type: Object as PropType<ProductListItemRead>,
    },
    week: { required: true, type: Object as PropType<YearWeek> },
    canEdit: { default: true, type: Boolean },
  },
  emits: ["openItem", "updateItem", "update:model-value"],
  data() {
    const store = useBaseStore();
    return {
      store,
      WeekDays,
      showMoveWeek: false,
      searchWeek: "",
      moveWeek: null as null | ProductListWeekRead,
      priorityOptions,
    };
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
  methods: {
    getDay(idx: number): string {
      const fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, "DD.MM");
    },
    ingUsingStr(ing: RecipeIngredientWithRecipeRead): string {
      const recipe = ing.recipe;
      if (!recipe) {
        return "";
      }

      const amounts = this.item?.amounts as ProductListItemAmounts;
      const ings = amounts[recipe.id] || [];

      const texts = ings.map((i) => {
        let r = String(i.amount) + " " + i.amount_type_str;
        if (i.is_main) {
          r += ", основной";
        }
        return r;
      });
      return texts.join(", ");
    },

    filterWeeks(val: string, update: CallableFunction) {
      // if (this.searchWeek == val) {
      //   update(() => {});
      //   return;
      // }
      this.searchWeek = val || "";
      const payload = {
        short: "1",
        search: this.searchWeek.replaceAll(".", ""),
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
        const payload = {
          pageSize: 20,
          search: search,
          fields: "id,title",
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
            this.handleErrors(err, "Ошибка загрузки ингредиентов");
          });
      });
    },
    filterIngredients(val: string, update: CallableFunction) {
      void this.loadIngredients(val).then(() => {
        void update();
      });
    },
    moveWeekDelta(delta: number) {
      const year = this.week.year.valueOf();
      let week = this.week.week.valueOf();

      week = week + delta;

      if (week < 0) {
        week = 54;
      } else if (week > 54) {
        week = 1;
      }

      const payload = {
        year: year,
        week: week,
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

      const item = Object.assign({}, this.item);

      item.week = this.moveWeek.id;
      this.$emit("updateItem", item, true);
      this.showMoveWeek = false;
      this.$emit("update:model-value", false);
    },
    getRecipeDays(recipe: RecipeRead | RecipeShort): null | string[] {
      if (!this.plan) {
        return null;
      }
      const plans = this.plan.plans.filter((p) => p.recipe.id == recipe?.id);
      return plans.map((p) => (p.day ? WeekDaysShort[p.day] : ("" as string)));
    },
  },
});
</script>

<style lang="scss">
.ing-day {
  min-width: 20px;
}
</style>
