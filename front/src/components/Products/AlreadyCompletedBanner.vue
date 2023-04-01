<template>
  <div :style="divStyle" />
  <q-item
    v-if="show"
    v-scroll="onScroll"
    class="bg-info text-white"
    :style="style"
  >
    <q-item-section avatar>
      <q-icon name="info" />
    </q-item-section>
    <q-item-section>Режим "отметить что уже есть"</q-item-section>
  </q-item>
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
        return ["position:fixed", "top: 50px;", "width: 100%;"]
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
      console.debug("scroll: ", position)
      this.fixedMode = position > 30
  }
  }
})
</script>