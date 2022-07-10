<template>
  <q-page class="flex flex-center">
    <div class="row justify-center items-center q-col-gutter-x-md">
      <q-icon name="restaurant" size="50px" color="primary" />
      <span class="text-bold text-h6"> База рецептов </span>
    </div>

    <div class="row">
      <q-list> </q-list>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'IndexPage',
});
</script>
