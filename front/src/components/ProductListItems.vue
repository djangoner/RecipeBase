<template>
  <q-item
    v-for="item of listItems"
    :key="item.id"
    class="cursor-pointer non-selectable column"
    :class="itemCls(item)"
    clickable
    @click="$emit('openItem', item)"
  >
    <div class="row no-wrap">
      <!-- Checkbox -->
      <q-checkbox
        v-model="item.is_completed"
        :color="item.already_completed?'info':'primary'"
        checked-icon="task_alt"
        unchecked-icon="radio_button_unchecked"
        size="lg"
        :disable="!canEdit"
        @update:model-value="$emit('updateItem', item)"
      />

      <!-- First column -->
      <div class="row column">
        <span class="text-subtitile2">
          <!-- Product title -->
          {{ item.title }}

          <!-- Manual ingredient -->
          <template
            v-if="
              !item.is_auto &&
                item.ingredient &&
                item.title.toLowerCase() !== item.ingredient.title.toLowerCase()
            "
          >
            ({{ item.ingredient.title }})
          </template>

          <!-- Product amount -->
          <template v-if="item.amount">
            (
            <template v-if="item.packs && item.ingredient.item_weight">
              ~{{ Math.ceil(item.packs) }}
              {{ item.ingredient.min_pack_size === 1000 ? "кг" : "шт" }}:
            </template>
            {{ item.amount }} {{ item.amount_type_str }}
            )
          </template>
          <template v-else-if="item.ingredients && item.ingredients.length > 0">
            (
            <span
              v-for="(sub_ing, index) of item.ingredients"
              :key="sub_ing.id"
            >
              {{ sub_ing.amount }} {{ sub_ing.amount_type_str
              }}<template v-if="index != item.ingredients.length - 1">,
              </template>
            </span>
            )
          </template>
          <template v-if="item.price_full">, ~{{ item.price_full }}₺</template>
        </span>
        <!-- First column bottom row, date -->
        <span
          class="text-body2"
          :class="item.day || item.day === 0 ? WeekDaysColors[item.day] : ''"
        >
          <q-icon
            v-if="item.is_auto"
            name="settings"
          >
            <q-tooltip>
              Этот рецепт был создан автоматически на основе плана на неделю
            </q-tooltip>
          </q-icon>
          <q-icon
            v-else
            name="edit"
          />
          <q-icon
            v-if="!item.is_auto && item.ingredient"
            name="restaurant"
          />

          <q-icon
            v-if="item?.ingredient?.description"
            class="q-ml-xs"
            color="primary"
            size="xs"
            name="notes"
          />

          <q-badge
            class="q-mx-sm q-py-xs"
            :color="item.priority ? priorityColors[item.priority] : ''"
          >
            <q-icon
              name="flag"
              size="10px"
            />
            <span class="q-ml-xs">
              {{ item.priority }}
            </span>
          </q-badge>
          <q-icon
            v-if="item.description"
            name="notes"
            size="17px"
            color="blue-grey"
          />

          {{ item.day || item.day === 0 ? getDay(item.day) : "" }}
          {{ item.day || item.day === 0 ? WeekDays[item.day] : "" }}

          <span
            v-if="isEdited(item)"
            class="text-teal"
          >
            [Изменено локально]
          </span>
        </span>
      </div>
    </div>

    <div
      v-if="item.amount_completed && item.amount"
      class="item__count row items-center no-wrap q-mx-md"
    >
      <span class="item__count-text">{{ item.amount_completed }} /
        {{ Math.ceil(item.packs || item.amount) }}
      </span>
      <q-linear-progress
        :value="item.amount_completed / Math.ceil(item.packs || item.amount)"
        class="col-grow"
      />
    </div>
  </q-item>
</template>

<script lang="ts">
import { date } from "quasar";
import { ProductListItemRead } from "src/client";
import { defineComponent, PropType } from "vue";
import {
  getDateOfISOWeek,
  WeekDays,
  YearWeek,
  WeekDaysColors,
  priorityColors,
} from "src/modules/WeekUtils";
import { getPackSuffix } from "src/modules/Utils";
import { productListGetChanged, ProductListItemSyncable } from "src/modules/ProductListSync";

export default defineComponent({
  props: {
    listItems: {
      required: true,
      type: Array as PropType<ProductListItemRead[]>,
    },
    week: { required: true, type: Object as PropType<YearWeek> },
    canEdit: { default: true, type: Boolean },
  },
  emits: ["openItem", "updateItem", "update:model-value"],

  data() {
    return {
      // listItems: null,
      WeekDays: WeekDays as { [key: number]: string },
      WeekDaysColors,
      changedItems: null as number[] |null,
      priorityColors,
    };
  },
  watch: {
    // listItems(val, oldVal) {
    //   if (val == oldVal) {
    //     return;
    //   }
    //   this.$emit('update:model-value', val);
    // },
    // modelValue(val, oldVal) {
    //   if (val == oldVal) {
    //     return;
    //   }
    //   this.listItems = val;
    // },
  },
  async created(){
    const items = await productListGetChanged(this.week.year, this.week.week)
    this.changedItems = items.map(i => i.idLocal || i.id)
  },
  methods: {
    getPackSuffix,
    getDay(idx: number): string | null {
      if (!this.week) {
        return null;
      }
      // console.debug(this.week, this.week.year, this.week.week);
      // let fday: Date = getDateOfISOWeek(this.week.year, this.week.week);
      const fday = getDateOfISOWeek(1, 2);
      fday.setDate(fday.getDate() + idx - 1);
      return date.formatDate(fday, "DD.MM");
    },
    intFormat(
      number: number,
      val1: string,
      val2: string,
      val3: string
    ): string {
      const n = number.toString();
      if (number > 10 && number < 20) {
        return val3;
      } else if (n.endsWith("1")) {
        return val1;
      } else if (n.endsWith("2") || n.endsWith("3") || n.endsWith("4")) {
        return val2;
      } else {
        return val3;
      }
      // return number;
    },
    isEdited(item: ProductListItemSyncable): boolean | undefined {
      // let isNotSynced = !!this.$q.localStorage.getItem('local_productlist_updated');
      const itemId = item.idLocal || item.id
      // console.debug("isChanged: ", item.is_changed, itemId, item)
      return item.is_changed || this.changedItems?.indexOf(itemId) !== -1
    },
    itemCls(item: ProductListItemRead): string | undefined {
      if (item?.is_completed && "dark" in this.$q) {
        return this.$q.dark.isActive ? "bg-grey-9" : "bg-grey-4";
      }
    },
  },
});
</script>

<style scoped lang="scss">
.item__count {
  &-text {
    min-width: 50px;
  }
}
</style>
