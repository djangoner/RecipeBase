<template>
  <!-- TODO: Two vertical blocks -->
  <q-tooltip
    class="cover rounded-borders text-black"
    :class="$q.dark.isActive ? 'bg-grey-7' : 'bg-grey-3'"
    anchor="center right"
    self="center left"
    :offset="[2, 0]"
    max-width="50vw"
    max-height="50vh"
    style="min-width: 300px;min-height: 300px;width: auto;height: auto;"
  >
    <h6 class="q-mt-none q-mb-sm text-subtitle1">
      <q-icon
        v-if="recipe.is_archived"
        name="archive"
        size="xs"
        color="primary"
      />
      {{ recipe.title }}
      <!-- Stars difficulty -->

      <div class="title-rating" v-if="recipe.difficulty">
        <q-icon
          v-for="i in recipe.difficulty"
          :key="i"
          size="xs"
          color="teal"
          name="star_rate"
        />
      </div>
    </h6>

    <h6
      v-if="recipe.last_cooked"
      class="q-mt-none q-mb-sm text-subtitle2"
    >
      Приготовлено {{ dateFormat(recipe.last_cooked) }} - {{ daysLeftStr(recipe.last_cooked) }}
      <template v-if="recipe.cooked_times">
        ({{ recipe.cooked_times }} раз)
      </template>
    </h6>

    <span class="q-my-sm text-subtitle2">Ингредиенты:
      <template v-if="recipe.price_part">({{ recipe.price_part }}₺ - <small class="text-grey">{{ recipe.price_full }}₺</small>)</template>
    </span>

    <div
      v-for="ing of recipe.ingredients"
      :key="ing.id"
    >
      {{ ing.ingredient.title }}: {{ ing.amount_grams }} ({{ ing.amount }}
      {{ ing.amount_type_str }})
    </div>

    <div v-if="recipe.ratings && recipe.ratings.length > 0">
      <span class="q-my-sm text-subtitle2">Рейтинг:</span>
      <table>
        <tbody>
          <tr
            v-for="rating of recipe.ratings"
            :key="rating.id"
          >
            <td>
              {{
                rating.user?.first_name
                  ? rating.user.first_name + ' ' + rating.user?.last_name
                  : rating.user.username
              }}
            </td>
            <td>
              <q-rating
                :model-value="rating?.rating + 1"
                :readonly="true"
                :icon="['thumb_down', 'star']"
                :color-selected="['grey', 'green-5']"
                :max="6"
                size="1.5em"
                color="primary"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="recipe.tags && recipe.tags.length > 0">
      <span class="q-my-sm text-subtitle2">Метки:</span>
      <div class="row q-col-gutter-sm">
        <div
          v-for="tag of recipe.tags"
          :key="tag.id"
        >
          <q-badge>{{ tag.title }}</q-badge>
        </div>
      </div>
    </div>

    <!-- <div v-if="recipe.comment">
      <span class="q-my-sm text-subtitle2">Комментарий:</span>
      <p style="white-space: pre-line">{{ recipe.comment }}</p>
    </div> -->
  </q-tooltip>
</template>

<script lang="ts">
import { RecipeRead } from 'src/client';
import { defineComponent, PropType } from 'vue';
import { date } from 'quasar';
import {pluralize} from 'src/modules/Utils'

export default defineComponent({
  props: {
    recipe: { required: true, type: Object as PropType<RecipeRead> },
  },
  data() {
    return {};
  },
  methods: {
    dateFormat(dt: Date | string): string {
      return date.formatDate(dt, 'YYYY.MM.DD');
    },
    daysLeft(dt: Date | string): number {
      return date.getDateDiff(new Date(), dt, "days")
    },
    daysLeftStr(dt: Date | string): string {
      const days = this.daysLeft(dt)
      const daysAbs = Math.abs(days)
      const daysPlural = pluralize(daysAbs, ["день", "дня", "дней"])
      let txBefore = "";
      let txAfter = "";
      if (days > 0){
        txAfter = daysPlural + " назад"
      } else if(days < 0){
        txBefore = "через"
        txAfter = daysPlural
      } else {
        txAfter = "сегодня"
      }
      return `${txBefore} ${daysAbs} ${txAfter}`.trim()

    }
  },
});
</script>


<style lang="scss" scoped>
.title {
  &-rating {
    white-space: nowrap;
    display: inline-block;
  }
}
</style>