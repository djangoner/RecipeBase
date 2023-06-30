<template>
  <q-select
    v-bind="$attrs"
    :model-value="currentText"
    fill-input
    hide-selected
    :autofocus="false"
    @input-value="onInput"
    @blur="onBlur"
  />
  <!-- {{ lastText }}|| {{ currentText }} -->
</template>

<script setup lang="ts">
import { ref } from 'vue';


const $emit = defineEmits(["input"])

const lastText = ref("")
const currentText = ref("")

function onBlur(){
  lastText.value = currentText.value
}

function onInput(text: string){
  currentText.value = text
  $emit("input", text)
}

function clear(){
  currentText.value = ""
}

defineExpose({clear})

</script>