<template>
  <q-card
    v-ripple
    class="recipe-card cursor-pointer q-hoverable relative-position"
    :class="[recipe.is_planned ? 'recipe-used' : '']"
    @click="openRecipe(recipe.id)"
  >
    <span class="q-focus-helper" />

    <!-- Main card content -->
    <q-card-section>
      <div
        class="flex justify-center items-center"
        style="min-height: 100px"
      >
        <!-- <q-icon name="restaurant_menu" size="50px" color="grey"></q-icon> -->
        <q-img
          :src="recipeImage"
          :srcset="recipeImageWebp"
          placeholder-src="/favicon.png"
          width="100%"
          height="200px"
          fit="cover"
          style="max-height: 200px"
        >
          <template #error>
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

    <recipe-card-tooltip :recipe="recipe" />
    <recipe-menu
      :recipe="recipe"
      @update-item="$emit('updateItem')"
    />
  </q-card>
</template>

<script setup lang="ts">
import recipeCardTooltip from "components/RecipeCardTooltip.vue"
import { RecipeRead } from "src/client"
import { computed, PropType } from "vue"
import { useRouter } from "vue-router"
import RecipeMenu from "./RecipeMenu.vue"

const props = defineProps({
  recipe: { required: true, type: Object as PropType<RecipeRead> },
})
const $emit = defineEmits(["updateItem"])
const $router = useRouter()

const recipeRawImage = computed(() => {
  return props.recipe.images? props.recipe.images[0] : null
})

const recipeImage = computed(() => {
  return recipeRawImage.value?.image_thumbnail || recipeRawImage.value?.image
})

const recipeImageWebp = computed(() => {
  return recipeRawImage.value?.image_thumbnail_webp || recipeRawImage.value?.image_thumbnail || recipeRawImage.value?.image
})

function openRecipe(id: number) {
  void $router.push({ name: "recipe", params: { id: id } })
}
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
