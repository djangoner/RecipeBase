<template>
  <!-- Recipe details -->
  <div class="q-mt-none">
    <q-input
      v-if="edit"
      v-model="recipe.title"
      label="Название рецепта *"
      :rules="[requiredRule]"
      filled
      :dense="dense"
    >
      <template #after>
        <q-btn
          v-if="exists && storeAuth.hasPerm('recipes.change_recipe')"
          icon="edit"
          flat
          @click="toggleEdit()"
        >
          <q-tooltip>Предпросмотр рецепта (изменения не будут применены!)</q-tooltip>
        </q-btn>
      </template>
    </q-input>
    <h4
      v-else
      class="text-center q-my-none"
    >
      <q-icon
        v-if="recipe.is_archived"
        class="q-mr-xs"
        name="archive"
        size="sm"
        color="primary"
      >
        <q-tooltip>Этот рецепт архивирован</q-tooltip>
      </q-icon>
      {{ recipe.title }}

      <q-icon
        name="help"
        color="grey"
        size="sm"
      >
        <recipe-card-tooltip :recipe="recipe" />
      </q-icon>

      <q-btn
        v-if="storeAuth.hasPerm('recipes.change_recipe')"
        icon="edit"
        flat
        @click="toggleEdit()"
      >
        <q-tooltip>Изменить рецепт</q-tooltip>
      </q-btn>

      <recipe-menu :recipe="recipe" />
    </h4>
  </div>

  <!-- Recipe source -->
  <div>
    <q-input
      v-if="edit"
      v-model="recipe.source_link"
      label="Источник рецепта"
      filled
      :dense="dense"
    />
    <h6
      v-else
      class="text-center q-my-none"
    >
      <q-btn
        v-if="recipe.source_link && recipe.source_link.startsWith('http')"
        :href="recipe.source_link"
        target="_blank"
        icon="open_in_new"
        size="sm"
        color="primary"
        no-caps
      >
        Открыть источник
      </q-btn>
      <h6
        v-else
        class="text-center q-my-none"
      >
        Источник: {{ recipe.source_link || "-" }}
      </h6>
    </h6>
  </div>

  <!-- Recipe tags -->
  <div
    v-if="edit | recipe.tags?.length"
    class="row recipe-tags items-center q-gutter-x-md"
  >
    <span class="text-subtitle2">Метки: </span>

    <recipe-tags
      v-model:recipeTags="recipe.tags"
      :edit="edit"
    />
  </div>

  <!-- Info -->

  <div>
    <recipe-difficulty
      v-model.number="recipe.difficulty"
      :edit="edit"
    />
  </div>

  <div>
    <q-input
      v-if="edit"
      v-model.number="recipe.portion_count"
      type="number"
      label="Количество порций"
      filled
      :dense="dense"
    />
    <h6
      v-else-if="recipe.portion_count"
      class="text-center q-my-none"
    >
      <q-icon
        name="pie_chart_outline"
        color="grey"
      />
      Порций: {{ recipe.portion_count || "-" }}
    </h6>
  </div>
  <div>
    <q-input
      v-if="edit"
      v-model.number="recipe.cooking_time"
      type="number"
      label="Время приготовления"
      hint="Примерное время приготовления в минутах"
      filled
      :dense="dense"
    />
    <h6
      v-else-if="recipe.cooking_time"
      class="text-center q-my-none"
    >
      <q-icon
        name="timer"
        color="grey"
      />
      Время приготовления: {{ recipe.cooking_time || "-" }}
    </h6>
  </div>
  <div>
    <q-input
      v-if="edit"
      v-model.number="recipe.preparation_time"
      type="number"
      label="Время подготовки"
      hint="Примерное время подготовки к приготовлению в минутах. Например: настаивание теста, размачивание нута итп."
      filled
      :dense="dense"
    />
    <h6
      v-else-if="recipe.preparation_time"
      class="text-center q-my-none"
    >
      <q-icon
        name="timer"
        color="grey"
      />
      Время подготовки: {{ recipe.preparation_time || "-" }}
    </h6>
  </div>
  <div
    v-if="edit"
    class="row q-col-gutter-md q-mt-md"
  >
    <q-toggle
      v-model="recipe.is_archived"
      label="Рецепт архивирован"
      dense
    />
  </div>

  <!-- Images carousel -->
  <div
    v-if="!edit"
    class="images-carousel q-py-md"
  >
    <recipe-images-view :images="recipe.images" />
  </div>

  <recipe-images-upload
    v-if="edit && exists && recipe.images"
    v-model="recipe.images"
  />
  <q-separator />

  <!-- Recipe content -->

  <div
    v-if="edit"
    class="q-py-md q-gutter-sm full-width"
  >
    <div class="row justify-between items-center q-my-sm">
      <h6 class="q-my-none">
        Содержание (изначальное, источник)
      </h6>
      <div class="row">
        <q-btn
          icon="o_find_in_page"
          :disable="recipe.ingredients.length > 0 && exists"
          flat
          dense
          @click="autorecognizeIngredients()"
        >
          <q-tooltip>
            Автоматическое распознавание ингредиентов.
            <br>
            (доступно только при пустом списке ингрединтов)
          </q-tooltip>
        </q-btn>
      </div>
    </div>
    <content-editor v-model="recipe.content_source" />
    <h6 class="q-my-sm">
      Содержание (редактированное)
    </h6>
    <content-editor v-model="recipe.content" />

    <h6 class="q-my-sm">
      Комментарий
    </h6>
    <q-input
      v-model="recipe.comment"
      type="textarea"
      label="Комментарий"
    />
  </div>
  <div v-else>
    <div v-if="recipe.content_source">
      <span class="text-h6 q-my-sm text-primary">Содержание (изначальное)</span>
      <div
        class="recipe-text"
        v-html="recipe.content_source"
      />
      <q-separator />
    </div>

    <div v-if="recipe.content">
      <span class="text-h6 q-my-sm text-primary">Содержание</span>

      <div
        class="recipe-text"
        v-html="recipe.content"
      />
      <q-separator />
    </div>
  </div>
  <q-input
    v-model="recipe.short_description"
    type="textarea"
    label="Короткое описание"
    hint="Отображается на карточке рецепта"
    :readonly="!edit"
  />
  <div v-if="!edit && recipe.comment">
    <span class="text-h6 q-my-sm text-primary">Комментарий</span>

    <div
      class="recipe-text format-spaces"
      v-html="recipe.comment"
    />
    <q-separator />
  </div>
</template>

<script lang="ts" setup>
import RecipeImagesView from "./RecipeImagesView.vue"
import { RecipeRead, RecognizedIngredients } from "src/client"
import { useAuthStore } from "src/stores/auth"
import { useBaseStore } from "src/stores/base"
import { ingAddDefault } from "src/modules/Models"
import { computed, PropType } from "vue"
import RecipeMenu from "src/components/RecipeMenu.vue"
import RecipeImagesUpload from "src/components/RecipeImagesUpload.vue"
import RecipeTags from "src/components/Recipes/RecipeTags.vue"
import ContentEditor from "src/components/Recipes/ContentEditor.vue"
import RecipeDifficulty from "./Fields/RecipeDifficulty.vue"
import RecipeCardTooltip from "../RecipeCardTooltip.vue"
import { useQuasar } from "quasar"

const requiredRule = (val: string | number) => !!val || "Обязательное поле"

const archivedOptions = [
  { label: "Не архивирован", value: false },
  { label: "Архивирован", value: true },
]

const props = defineProps({
  edit: {
    type: Boolean,
    default: false,
  },
  modelValue: {
    type: Object as PropType<RecipeRead>,
    default: null,
    required: false,
  },
})

const $emit = defineEmits(["update:model-value", "update:edit"])
const $q = useQuasar()
const store = useBaseStore()
const storeAuth = useAuthStore()

const recipe = computed({
  get() {
    return props.modelValue
  },
  set(val: RecipeRead) {
    $emit("update:model-value", val)
  },
})
const dense = computed(() => true)
const exists = computed(() => Boolean(recipe.value?.id))
function toggleEdit() {
  $emit("update:edit", !props.edit)
}

function autorecognizeIngredients(){
  console.debug("Auto recognize ingredients")
  const prom = store.autorecognizeIngredients({text: recipe.value.content_source})
  $q.loading.show({
    message: "Распознавание ингредиентов..."
  })

  void prom.then((resp: RecognizedIngredients) => {
    const ings = resp.result
    console.debug("Auto recognized ingredients: ", ings, resp)
    if (ings && ings.length > 0){

      if (recipe.value.ingredients){
        recipe.value.ingredients.length = 0
        ings.forEach(ingredient => {
            recipe.value.ingredients.push(Object.assign({}, ingAddDefault, ingredient))
          });
      }

      $q.notify({
        type: 'positive',
        message: "Ингредиенты успешно распознаны"
      })
    } else {
      $q.notify({
        type: 'warning',
        message: "Ингредиенты не распознаны"
      })
    }
  }).finally(() => {
    $q.loading.hide()
  })
}

</script>
