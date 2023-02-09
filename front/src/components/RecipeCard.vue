<template>
  <q-card
    class="recipe-card cursor-pointer q-hoverable relative-position"
    :class="[recipe.is_planned ? 'recipe-used' : '']"
    v-ripple
    @click="openRecipe(recipe.id)"
  >
    <span class="q-focus-helper"></span>

    <!-- Main card content -->
    <q-card-section>
      <div class="flex justify-center items-center" style="min-height: 100px">
        <!-- <q-icon name="restaurant_menu" size="50px" color="grey"></q-icon> -->
        <q-img
          :src="
            recipe?.images && recipe.images.length > 0
              ? recipe.images[0]?.image
              : '/favicon.png'
          "
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
            <div
              class="absolute-bottom text-subtitle1 text-center"
              :class="[recipe.is_planned ? 'text-underline' : '']"
            >
              {{ recipe.title }}
            </div>
          </template>
          <div
            class="absolute-bottom text-subtitle1 text-center"
            :class="[recipe.is_planned ? 'text-underline' : '']"
          >
            {{ recipe.title }}
          </div>
        </q-img>
      </div>
    </q-card-section>

    <q-card-section>
      <span class="text-subtitle2">{{ recipe.short_description_str }}</span>
    </q-card-section>

    <!-- Aside info tooltip -->

    <recipe-card-tooltip :recipe="recipe"></recipe-card-tooltip>
    <recipe-menu :recipe="recipe" @updateItem="$emit('updateItem')"></recipe-menu>
  </q-card>
</template>

<script lang="ts">
import recipeCardTooltip from 'components/RecipeCardTooltip.vue';
import { date } from 'quasar';
import { RecipeRead } from 'src/client';
import { defineComponent, PropType } from 'vue';
import RecipeMenu from './RecipeMenu.vue';

export default defineComponent({
  props: {
    recipe: { required: true, type: Object as PropType<RecipeRead> },
  },
  emits: ['updateItem'],
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { recipeCardTooltip, RecipeMenu },
  data() {
    return {};
  },
  methods: {
    dateFormat(dt: Date | string): string {
      return date.formatDate(dt, 'YYYY.MM.DD');
    },
    openRecipe(id: number) {
      void this.$router.push({ name: 'recipe', params: { id: id } });
    },
  },
});
</script>

<style lang="scss" scoped>
.recipe-card {
  &.recipe-used {
    & > .q-focus-helper {
      background: currentColor;
      opacity: 0.1;
    }
  }
}
</style>
