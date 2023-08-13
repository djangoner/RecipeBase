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
    style="min-width: 300px; min-height: 300px; width: auto; height: auto"
    @before-show="onShow"
  >
    <h6 class="q-mt-none q-mb-sm text-subtitle1">
      <q-icon
        v-if="isLoading"
        name="pending"
        size="xs"
        color="primary"
      />
      <q-icon
        v-if="recipe.is_archived"
        name="archive"
        size="xs"
        color="primary"
      />
      {{ recipe.title }}
      <!-- Stars difficulty -->

      <div
        v-if="recipe.difficulty"
        class="title-rating"
      >
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

    <span
      v-if="recipe.ingredients?.length"
      class="q-my-sm text-subtitle2"
    >Ингредиенты:
      <template v-if="recipe.price_part">({{ recipe.price_part }}₺ - <small class="text-grey">{{ recipe.price_full }}₺</small>)</template>
    </span>

    <div
      v-for="ing of recipe.ingredients"
      :key="ing.id"
    >
      {{ ing.ingredient.title }}: {{ ing.amount_grams }} ({{ ing.amount }} {{ ing.amount_type_str }})
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
              {{ rating.user?.first_name ? rating.user.first_name + " " + rating.user?.last_name : rating.user.username }}
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

<script lang="ts" setup>
import { RecipeRead, RecipeShort } from "src/client"
import { computed, PropType, ref } from "vue"
import { date } from "quasar"
import { pluralize } from "src/modules/Utils"
import { useBaseStore } from "src/stores/base"
import { useCacheStore } from "src/stores/cache"
import { promiseSetLoading } from "src/modules/StoreCrud"

const props = defineProps({
  recipe: { required: true, type: Object as PropType<RecipeRead | RecipeShort> },
  loadRecipe: { type: Boolean, default: true },
})

const store = useBaseStore()
const storeCache = useCacheStore()

const isLoading = ref(false)

const recipe = computed(() => {
  if (props.loadRecipe) {
    const cachedRecipe = storeCache.getCached(cacheKey.value)
    if (cachedRecipe) {
      return cachedRecipe as RecipeRead
    }
  }
  return props.recipe
})

const cacheKey = computed(() => {
  return { recipe: props.recipe.id }
})

function dateFormat(dt: Date | string): string {
  return date.formatDate(dt, "YYYY.MM.DD")
}
function daysLeft(dt: Date | string): number {
  return date.getDateDiff(new Date(), dt, "days")
}
function daysLeftStr(dt: Date | string): string {
  const days = daysLeft(dt)
  const daysAbs = Math.abs(days)
  const daysPlural = pluralize(daysAbs, ["день", "дня", "дней"])
  let txBefore = ""
  let txAfter = ""
  if (days > 0) {
    txAfter = daysPlural + " назад"
  } else if (days < 0) {
    txBefore = "через"
    txAfter = daysPlural
  } else {
    txAfter = "сегодня"
  }
  return `${txBefore} ${daysAbs} ${txAfter}`.trim()
}

function onShow() {
  loadRecipe()
}

function loadRecipe() {
  if (!props.loadRecipe || !props.recipe?.id || isLoading.value) {
    return
  }
  const cacheKey = { recipe: props.recipe.id }
  if (storeCache.getCached(cacheKey)) {
    return
  }
  const omit = "content,content_source,recommendations_ingredients,recommendations_recipes,recommendations_tags"

  // console.debug("Loading recipe #" + props.recipe.id.toString())
  const prom = store.loadRecipe(props.recipe.id, omit)

  promiseSetLoading(prom, isLoading)
  void prom.then((data) => {
    storeCache.setCached(cacheKey, data)
    // console.debug("Caching recipe #" + props.recipe.id.toString())
  })
}
</script>

<style lang="scss" scoped>
.title {
  &-rating {
    white-space: nowrap;
    display: inline-block;
  }
}
</style>
