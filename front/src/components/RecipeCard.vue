<template>
  <q-card class="cursor-pointer q-hoverable" v-ripple @click="openRecipe(recipe.id)">
    <span class="q-focus-helper"></span>
    <q-card-section>
      <div class="flex justify-center items-center" style="min-height: 100px">
        <!-- <q-icon name="restaurant_menu" size="50px" color="grey"></q-icon> -->
        <q-img
          :src="recipe.images ? recipe.images[0]?.image : null"
          width="100%"
          height="100px"
          fit="cover"
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
  </q-card>
</template>

<script>
export default {
  props: {
    modelValue: { required: true },
  },
  data() {
    return {};
  },
  methods: {
    openRecipe(id) {
      this.$router.push({ name: 'recipe', params: { id: id } }).catch((e) => {});
    },
  },
  computed: {
    recipe() {
      return this.modelValue;
    },
  },
};
</script>
