<template>
  <div :style="divStyle" />
  <q-banner
    v-if="show"
    v-scroll="onScroll"
    class="bg-info text-white"
    :style="style"
  >
    <template #avatar>
      <q-icon
        name="info"
        size="md"
      />
    </template>

    Режим "отметить что уже есть"
  </q-banner>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    show: {
      type: Boolean,
      required: true,
    }
  },
  data(){
    return {fixedMode: false,}
  },
  computed: {
    style(){
      if (this.fixedMode){
        return ["position:fixed", "top: 50px;", "width: 100%;", "z-index: 2"]
      }
      return {}
    },
    divStyle(){
      if (this.fixedMode){
        return ["height: 50px;"]
      }
      return []
    }
  },
  methods: {
    onScroll (position: number) {
      this.fixedMode = position > 30
  }
  }
})
</script>