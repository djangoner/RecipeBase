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
          :src="recipe.images ? recipe.images[0]?.image : null"
          width="100%"
          height="200px"
          fit="cover"
          style="max-height: 200px"
        >
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
      class="fit overflow-auto bg-grey-3 rounded-borders text-black"
      anchor="center right"
      self="center left"
      :offset="[2, 0]"
      max-width="300px"
      max-height="300px"
    >
      <h6 class="q-mt-none q-mb-sm text-subtitle1">{{ recipe.title }}</h6>

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
                  :modelValue="rating?.rating"
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

      <div v-if="recipe.comment">
        <span class="q-my-sm text-subtitle2">Комментарий:</span>
        <p style="white-space: pre-line">{{ recipe.comment }}</p>
      </div>
    </q-tooltip>
  </q-card>
</template>

<script>
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
  },
  computed: {},
};
</script>

<style lang="scss" scoped></style>
