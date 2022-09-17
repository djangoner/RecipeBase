<template>
  <q-card
    class="cursor-pointer q-hoverable relative-position"
    v-ripple
    @click="openRecipe(recipe.id)"
  >
    <span class="q-focus-helper"></span>

    <!-- Main card content -->
    <q-card-section>
      <div class="flex justify-center items-center" style="min-height: 100px">
        <!-- <q-icon name="restaurant_menu" size="50px" color="grey"></q-icon> -->
        <q-img
          :src="recipe.images.length > 0 ? recipe.images[0]?.image : '/favicon.png'"
          placeholder-src="/favicon.png"
          width="100%"
          height="200px"
          fit="cover"
          style="max-height: 200px"
        >
          <template v-slot:error>
            <div class="absolute-full flex flex-center bg-negative text-white">
              Ошибка загрузки
            </div>
            <div class="absolute-bottom text-subtitle1 text-center">
              {{ recipe.title }}
            </div>
          </template>
          <div class="absolute-bottom text-subtitle1 text-center">
            {{ recipe.title }}
          </div>
        </q-img>
      </div>
    </q-card-section>

    <q-card-section>
      <span class="text-subtitle2">{{ recipe.short_description }}</span>
    </q-card-section>

    <!-- Aside info tooltip -->
    <q-tooltip
      class="fit overflow-auto rounded-borders text-black"
      :class="$q.dark.isActive ? 'bg-grey-7' : 'bg-grey-3'"
      anchor="center right"
      self="center left"
      :offset="[2, 0]"
      max-width="300px"
      max-height="300px"
    >
      <h6 class="q-mt-none q-mb-sm text-subtitle1">{{ recipe.title }}</h6>
      <h6 class="q-mt-none q-mb-sm text-subtitle2" v-if="recipe.last_cooked">
        Приготовлено {{ dateFormat(recipe.last_cooked) }}
        <template v-if="recipe.cooked_times">({{ recipe.cooked_times }} раз)</template>
      </h6>

      <span class="q-my-sm text-subtitle2">Ингредиенты:</span>

      <div v-for="ing of recipe.ingredients" :key="ing.id">
        {{ ing.ingredient.title }}: {{ ing.amount_grams }} ({{ ing.amount }}
        {{ ing.amount_type_str }})
      </div>

      <div v-if="recipe.ratings && recipe.ratings.length > 0">
        <span class="q-my-sm text-subtitle2">Рейтинг:</span>
        <table>
          <tbody>
            <tr v-for="rating of recipe.ratings" :key="rating.id">
              <td>
                {{
                  rating.user?.first_name
                    ? rating.user.first_name + ' ' + rating.user?.last_name
                    : rating.user.username
                }}
              </td>
              <td>
                <q-rating
                  :modelValue="rating?.rating + 1"
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
          <div v-for="tag of recipe.tags" :key="tag.id">
            <q-badge>{{ tag.title }}</q-badge>
          </div>
        </div>
      </div>

      <div v-if="recipe.comment">
        <span class="q-my-sm text-subtitle2">Комментарий:</span>
        <p style="white-space: pre-line">{{ recipe.comment }}</p>
      </div>
    </q-tooltip>
  </q-card>
</template>

<script>
import { date } from 'quasar';
export default {
  props: {
    recipe: { required: true },
  },
  data() {
    return {};
  },
  methods: {
    openRecipe(id) {
      this.$router.push({ name: 'recipe', params: { id: id } }).catch((e) => {});
    },
    dateFormat(dt) {
      return date.formatDate(dt, 'YYYY.MM.DD');
    },
  },
  computed: {},
};
</script>

<style lang="scss" scoped></style>
