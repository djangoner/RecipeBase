<template>
  <div class="col col-xs-6 col-sm-6 col-md-3">
    <q-card
      @click="$emit('cardClick')"
      class="row cursor-pointer q-hoverable no-wrap"
      :class="[
        mobile ? 'q-px-xs' : 'q-px-md',
        mobile ? 'justify-start' : 'justify-between',
      ]"
      flat
      bordered
      v-ripple
    >
      <span class="q-focus-helper"></span>
      <q-card-section :class="[mobile && 'q-px-sm']">
        <q-icon :name="icon" :size="mobile ? 'sm' : 'lg'" :color="iconColor"></q-icon>
      </q-card-section>

      <q-space v-if="mobile" />

      <q-card-section class="text-right">
        <b class="text-h6">{{ value }}</b>
        <br />
        <span>{{ title }}</span>
      </q-card-section>
    </q-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

const component = defineComponent({
  props: {
    icon: { type: String, default: 'home' },
    iconColor: { type: String, default: 'light-blue-5' },
    title: { type: String, default: 'Card' },
    value: { type: [String, Number], default: '-' },
  },
  emits: ['cardClick'],
  data() {
    return {};
  },
  methods: {},
  computed: {
    mobile(): boolean {
      return this.$q.screen.lt.md;
    },
  },
});

export default component;
</script>
