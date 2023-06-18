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
          <product-list-item-checkbox
            v-model="item"
            :disable="!canEdit"
            @update:model-value="$emit('updateItem', $event)"
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
                <q-tooltip> Этот рецепт был создан автоматически на основе плана на неделю </q-tooltip>
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
            <q-tooltip> Продукт уже есть и его не требуется покупать </q-tooltip>
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
          <ingredient-used-recipes :item="item">
            <template v-if="item.price_full">
              <div>Цена {{ item.price_full }}₺ (~{{ item.price_part }}₺ необходимо)</div>
            </template>
          </ingredient-used-recipes>
        </div>

        <div class="q-my-md q-col-gutter-x-md row">
          <div>
            <product-list-item-move-week
              v-if="item"
              v-model="item.week"
              :week="week"
              :can-edit="canEdit && !item.is_auto"
              @update:model-value="itemMoveWeek(item)"
            />
          </div>
          <div>
            <q-btn
              v-if="isOnline && item?.ingredient"
              :to="{ name: 'ingredient', params: { id: item?.ingredient?.id } }"
              label="Открыть ингредиент"
              icon="open_in_new"
              size="sm"
              color="primary"
              no-caps
              dense
              unelevated
            />
          </div>
        </div>

        <!-- Product list ingredient description -->
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
            :src="item.ingredient.image_thumbnail || item.ingredient.image"
            :srcset="item.ingredient.image_thumbnail_webp"
            fit="contain"
            style="max-height: 400px"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import IngredientUsedRecipes from "./Products/IngredientUsedRecipes.vue"
import ProductListItemCheckbox from "./Products/ProductListItemCheckbox.vue"
import ProductListItemMoveWeek from "./Products/ProductListItemMoveWeek.vue"
import { WeekDays, YearWeek } from "src/modules/WeekUtils"
import { computed, PropType } from "vue"
import { priorityOptions } from "src/modules/Globals"
import { ProductListItemRead } from "src/client"
import AmountTypeSelect from "./Products/AmountTypeSelect.vue"
import AmountCompletedInput from "./Products/AmountCompletedInput.vue"
import IngredientSelect from "./Recipes/IngredientSelect.vue"
import {isOnline} from 'src/modules/isOnline'

const props = defineProps({
  modelValue: {
    required: false,
    default: undefined,
    type: Object as PropType<ProductListItemRead>,
  },
  week: { required: true, type: Object as PropType<YearWeek> },
  canEdit: { default: true, type: Boolean },
})

const $emit = defineEmits(["openItem", "updateItem", "update:model-value"])

const item = computed(() => {
  return props.modelValue
})

const weekDaysOptions = computed(() => {
  return Object.entries(WeekDays).map(([id, name]) => {
    return { id: parseInt(id), name: name }
  })
})

function itemMoveWeek(item: ProductListItemRead) {
  $emit("updateItem", item, true)
  $emit("update:model-value", false)
}
</script>

<style lang="scss">
.ing-day {
  min-width: 20px;
}
</style>
