<template>
  <q-carousel
    v-if="(images || [])?.length > 0"
    v-model="slide"
    v-model:fullscreen="fullscreen"
    :autoplay="autoplay"
    :height="$q.screen.gt.md ? '450px' : '250px'"
    transition-prev="slide-right"
    transition-next="slide-left"
    animated
    navigation
    infinite
    arrows
    @mouseenter="autoplay = false"
    @mouseleave="autoplay = true"
  >
    <template #control>
      <q-carousel-control
        position="bottom-right"
        :offset="[18, 18]"
      >
        <q-btn
          push
          round
          dense
          color="white"
          text-color="primary"
          :icon="fullscreen ? 'fullscreen_exit' : 'fullscreen'"
          @click="fullscreen = !fullscreen"
        />
      </q-carousel-control>
    </template>
    <q-carousel-slide
      v-for="(img, idx) of images"
      :key="img.id"
      :name="idx + 1"
      :img-src="img.image"
    />
  </q-carousel>
</template>


<script lang="ts">
import { RecipeImage } from 'src/client';
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  props: {
    images: {type: Array as PropType<RecipeImage[]>, default: null, required: false}
  },
  data(){
    return {
      slide: 1,
      autoplay: true,
      fullscreen: false,
    }
  },
})
</script>