<template>
  <q-item
    clickable
    dense
    :inset-level="1"
  >
    <!-- Icon -->
    <q-item-section avatar>
      <q-icon
        v-if="rec.accepted"
        name="done"
        color="positive"
        size="sm"
      />
      <q-icon
        v-else
        :name="iconName"
        color="grey"
        size="sm"
      />
    </q-item-section>

    <!-- Title -->
    <q-item-section>
      <q-item-label :class="{'text-positive':rec.accepted}">
        {{ sectionTitle }}
      </q-item-label>
      <q-item-label caption>
        {{ sectionText }}
      </q-item-label>


      <template v-if="rec.recipe">
        <recipe-card-tooltip
          :recipe="rec.recipe"
        />
      </template>
    </q-item-section>

    <!-- Actions -->
    <q-item-section side>
      <div
        class="row q-gutter-x-sm"
      >
        <template v-if="rec.accepted">
          <q-btn
            v-if="canCancell"
            label="Отменить"
            icon="undo"
            color="negative"
            size="sm"
            dense
            no-caps
            unelevated
            @click="onCancell"
          />
        </template>
        <template v-else>
          <q-btn
            v-if="rec.recipe_tag"
            label="Найти"
            icon="search"
            color="primary"
            size="sm"
            dense
            no-caps
            unelevated
          />
          <q-btn
            v-else
            label="Добавить"
            icon="add"
            color="positive"
            size="sm"
            dense
            no-caps
            unelevated
            :loading="saving"
            @click="runPerform()"
          />
        </template>
      </div>
    </q-item-section>
  </q-item>
</template>


<script setup lang="ts">
import RecipeCardTooltip from '../RecipeCardTooltip.vue'
import { useQuasar } from 'quasar';
import { Recommendations } from 'src/client';
import { YearWeek } from 'src/modules/Globals';
import { promiseSetLoading } from 'src/modules/StoreCrud';
import { useBaseStore } from 'src/stores/base';
import { computed, PropType, ref } from 'vue';


const props = defineProps({
  week: {
    type: Object as PropType<YearWeek>,
    required: true,
  },
  recommendation: {
    type: Object as PropType<Recommendations>,
      required: true,
  }
})

const $emit = defineEmits(["updated"])
const $q = useQuasar()

const store = useBaseStore()

const saving = ref(false)

const rec = computed(() => props.recommendation)

const iconName = computed(() => {
  if (rec.value.recipe){
    return "menu_book"
  } else if (rec.value.recipe_tag){
    return "label"
  } else if (rec.value.ingredient){
    return "shopping_basket"
  }
  return "menu_book"
})

const sectionTitle = computed(() => {
  if (rec.value.recipe){
    return rec.value.recipe.title
  } else if (rec.value.recipe_tag){
    return rec.value.recipe_tag.title
  } else if (rec.value.ingredient){
    const ingId = rec.value.ingredient.ingredient
    const ing = getIngredient(ingId)
    return ing?.title
  }
  return "?"
})

const sectionText = computed(() => {
  if (rec.value.ingredient){
    const ing = rec.value.ingredient
    return `${ing.amount} ${ing.amount_type_str || ''}`
  }
  return ""
})

const canCancell = computed(() => {
  return rec.value.ingredient
})


function onCancell(){
  $q
    .dialog({
      title: "Подтверждение",
      message: "Вы уверены что хотите отменить рекомендацию?",
      cancel: true,
      persistent: true,
    })
    .onOk(() => {
      runCancell()
    });
}

function getIngredient(id: number){
  return store.ingredients?.find(i => i.id == id)
}


function runPerform(){
  saving.value = true

  const payload = {
    year: props.week.year,
    week: props.week.week,
    recommendation: rec.value.hash,
  }
  console.debug("Accepting recommendation: ", payload)

  const prom = store.acceptWeekRecommendation(payload)

  void prom.then(() => {
    $emit("updated")
    $q.notify({
      type: "positive",
      caption: "Рекомендация успешно принята"
    })
  })

  promiseSetLoading(prom, saving)
}

function runCancell(){
  saving.value = true

  const payload = {
    year: props.week.year,
    week: props.week.week,
    recommendation: rec.value.hash,
  }
  console.debug("Cancelling recommendation: ", payload)

  const prom = store.cancellWeekRecommendation(payload)

  void prom.then(() => {
    $emit("updated")
    $q.notify({
      type: "positive",
      caption: "Рекомендация успешно отменена"
    })
  })

  promiseSetLoading(prom, saving)
}


</script>