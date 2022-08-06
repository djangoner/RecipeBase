<template>
  <q-page class="flex column q-gutter-y-lg">
    <div class="col-grow flex column flex-center q-col-gutter-y-lg">
      <div class="row justify-center items-center q-gutter-x-md">
        <q-icon name="restaurant" size="50px" color="primary" />
        <span class="text-bold text-h6"> База рецептов </span>
      </div>

      <div class="row">
        <q-list>
          <q-item :to="{ name: 'index' }"
            ><q-item-section avatar><q-icon name="home"></q-icon></q-item-section>
            <q-item-section>Главная</q-item-section>
          </q-item>
          <q-item :to="{ name: 'recipes' }"
            ><q-item-section avatar><q-icon name="article"></q-icon></q-item-section>
            <q-item-section>Рецепты</q-item-section>
          </q-item>
          <q-item :to="{ name: 'week_plan' }"
            ><q-item-section avatar
              ><q-icon name="calendar_month"></q-icon
            ></q-item-section>
            <q-item-section>План</q-item-section>
          </q-item>
          <q-item :to="{ name: 'product_list' }"
            ><q-item-section avatar
              ><q-icon name="shopping_basket"></q-icon
            ></q-item-section>
            <q-item-section>Список продуктов</q-item-section>
          </q-item>
        </q-list>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'IndexPage',
});
</script>
