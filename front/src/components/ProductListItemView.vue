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

        <ingredient-select
          v-model="item.ingredient"
          label="Ингредиент"
          clearable
          :required="false"
          :preload-all="false"
          :readonly="item.is_auto || !canEdit"
          @update:model-value="$emit('updateItem', item)"
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
            <product-list-item-move-week
              v-if="item"
              :item="item"
              :week="week"
              :can-edit="canEdit"
              @update:item="$emit('updateItem', $event, true)"
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
</template>

<script lang="ts">
import ProductListItemMoveWeek from './Products/ProductListItemMoveWeek.vue'
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
import IngredientSelect from './Recipes/IngredientSelect.vue';

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
  components: { AmountTypeSelect, AmountCompletedInput, ProductListItemMoveWeek, IngredientSelect },
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
    weekDaysOptions() {
      return Object.entries(this.WeekDays).map(([id, name]) => {
        return { id: parseInt(id), name: name };
      });
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
    itemMoveWeek(item: ProductListItemRead) {
      this.$emit("updateItem", item, true);
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
