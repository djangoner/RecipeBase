<template>
  <q-banner
    v-if="show"
    class="bg-warning text-white"
    inline-actions
    rounded
  >
    <template #avatar>
      <q-icon
        name="warning"
        size="md"
      />
    </template>
    <template #action>
      <q-btn
        flat
        label="Обновить"
        @click="$emit('reload')"
      />
    </template>

    Возможно список продуктов не актулен
  </q-banner>
</template>

<script setup lang="ts">
defineProps({
  show: {
    type: Boolean,
    required: true,
  }
})
defineEmits(["reload"])
</script>