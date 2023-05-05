<template>
  <div class="q-my-sm">
    <div class="text-h6 text-center q-mb-sm">
      Игредиенты:
    </div>

    <q-table
      v-if="(recipe?.ingredients || [])?.length > 0 || edit"
      class="no-bottom"
      :rows="recipe.ingredients"
      :columns="ingredientsColumns"
      :rows-per-page-options="[0]"
      :hide-pagination="true"
      flat
      dense
    >
      <template #bottom />
      <!-- Custom fields -->

      <template #body-cell-title="slotScope">
        <td
          class="text-right"
          style="width: 50px"
        >
          <ingredient-select
            v-if="edit"
            v-model:ingredient="slotScope.row.ingredient"
          />
          <span v-else>{{ slotScope.value }}</span>
        </td>
      </template>

      <template #body-cell-amount_rec="slotScope">
        <td
          class="text-right"
          style="width: 50px"
        >
          <q-input
            v-if="edit"
            v-model.number="slotScope.row.amount"
            type="number"
            step="0.01"
            dense
            required
          >
            <q-tooltip> Единица измерения: {{ slotScope.row.amount_type_str }} </q-tooltip>
          </q-input>
          <span v-else>{{ slotScope.value }}</span>
        </td>
      </template>

      <template #body-cell-is_main="slotScope">
        <td
          class="text-right"
          style="width: 30px"
        >
          <q-checkbox
            v-model="slotScope.row.is_main"
            :disable="!edit"
            size="sm"
          />
        </td>
      </template>

      <!-- Custom columns -->
      <template
        v-if="edit"
        #body-cell-amount_type="slotProps"
      >
        <q-td
          class="q-py-none"
          style="width: 120px; max-width: 120px"
        >
          <amount-type-select
            v-if="edit"
            v-model="slotProps.row.amount_type"
            :label="null"
          />
        </q-td>
      </template>
      <template
        v-if="edit"
        #body-cell-actions="slotProps"
      >
        <q-td
          class="q-py-none"
          style="width: 50px"
        >
          <div class="row justify-around">
            <q-btn
              icon="delete"
              color="negative"
              size="xs"
              dense
              @click="askRemoveIngredient(slotProps.row)"
            />
          </div>
        </q-td>
      </template>

      <!-- Bottom row -->
      <template
        v-if="edit"
        #bottom-row
      >
        <q-tr>
          <td colspan="3">
            <ingredient-select
              v-model:ingredient="addIngredientSelect"
              label="Добавить ингредиент"
              :required="false"
            />
          </td>
        </q-tr>
      </template>
    </q-table>

    <div
      v-else
      class="flex justify-center items-center"
      style="height: 100px"
    >
      <h6 class="text-bold">
        Игредиенты не указаны
      </h6>
    </div>
  </div>
</template>

<script setup lang="ts">
import AmountTypeSelect from "../Products/AmountTypeSelect.vue"
import IngredientSelect from "./IngredientSelect.vue"
import { IngredientRead, RecipeIngredientRead, RecipeRead } from "src/client"
import { computed, PropType, Ref, ref, watch } from "vue"
import { useQuasar } from "quasar"

const $emit = defineEmits(["update:recipe"])
const $q = useQuasar()

const addIngredientSelect: Ref<IngredientRead | undefined> = ref(undefined)

const props = defineProps({
  recipe: {
    type: Object as PropType<RecipeRead>,
    required: true,
  },
  edit: {
    type: Boolean,
    required: false,
  },
})

const ingredientsColumnsRaw = [
  {
    name: "title",
    label: "Название",
    field: (row: RecipeIngredientRead) => row.ingredient?.title,
    required: true,
    sortable: true,
    style: "width: 50px",
  },
  // {
  //   name: 'amount_type',
  //   label: 'Ед. изм.',
  //   field: (row) => row.amount_type,
  //   required: true,
  //   sortable: true,
  //   style: 'width: 20px',
  // },
  {
    name: "amount_rec",
    label: "Вес (рецепт)",
    field: (row: RecipeIngredientRead) => String(row.amount) + "  (" + row.amount_type_str + ")",
    required: true,
    sortable: true,
    style: "width: 20px",
  },
  {
    name: "amount_g",
    label: "Вес (гр.)",
    field: (row: RecipeIngredientRead) => (row.amount_grams ? String(row.amount_grams) + " гр." : "-"),
    required: true,
    sortable: true,
    style: "width: 30px",
  },
  {
    name: "is_main",
    label: "Основной",
    field: "is_main",
    required: true,
    sortable: true,
    style: "width: 30px",
  },
]

const ingAddDefault = {
  select: null as { id: number | null; title: string } | null,
  amount: null,
  amount_type: "g",
  is_main: false,
}

const ingredientsColumns = computed(() => {
  const column_actions = {
    name: "actions",
    label: "Действия",
    field: () => "",
    required: true,
    sortable: false,
    style: "width: 75px",
  }
  const column_amount_type = {
    name: "amount_type",
    label: "Единица измерения",
    field: () => "",
    required: true,
    sortable: false,
    style: "width: 120px",
  }
  let columns = ingredientsColumnsRaw.slice()

  if (props.edit) {
    columns.push(column_actions)
    columns.splice(1, 0, column_amount_type)
  } else {
    columns = columns?.filter((i) => i.name !== column_actions.name && i.name !== column_amount_type.name)
  }

  return columns
})

function updateIngredients(ings: RecipeIngredientRead[]) {
  const newRecipe = Object.assign({}, props.recipe)
  newRecipe.ingredients = ings
  console.debug("Update recipe: ", newRecipe)
  $emit("update:recipe", newRecipe)
}

function addIngredient(ingredient?: IngredientRead) {
  if (!ingredient) {
    if (!addIngredientSelect.value) return
    ingredient = addIngredientSelect.value
  }

  console.debug("Add ingredient: ", ingredient)

  const newIngredient = Object.assign({}, ingAddDefault, {
    ingredient: ingredient,
  })

  // @ts-expect-error new ingredient creation
  updateIngredients([].concat(props.recipe.ingredients, newIngredient))
  addIngredientSelect.value = undefined
}

function removeIngredient(row: RecipeIngredientRead) {
  console.debug("Remove ingredient: ", row)
  updateIngredients(
    props.recipe?.ingredients?.filter((t) => {
      return t != row
    }) || []
  )
}

function askRemoveIngredient(row: RecipeIngredientRead) {
  if (!props.recipe) {
    return
  }

  console.debug("Ask Remove ingredient: ", row)
  $q.dialog({
    title: "Подтверждение удаления ингредиента",
    message: `Вы уверены что хотите удалить ингредиент '${row?.ingredient?.title || "Новый ингредиент"}' ?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    console.debug("Remove ingredient confirmed")
    if (!props.recipe) {
      return
    }
    removeIngredient(row)
  })
}

watch(addIngredientSelect, (val) => {
  if (val) {
    addIngredient(val)
  }
})
</script>
