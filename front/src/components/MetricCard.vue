<template>
  <div class="col col-xs-6 col-sm-6 col-md-3">
    <q-card
      v-ripple
      class="row cursor-pointer q-hoverable no-wrap"
      :class="[
        mobile && 'compact',
        mobile ? 'q-px-xs' : 'q-px-md',
        mobile ? 'justify-start' : 'justify-between',
      ]"
      flat
      bordered
      @click="$emit('cardClick')"
    >
      <span class="q-focus-helper" />
      <q-card-section :class="[mobile && 'q-px-sm']">
        <q-icon
          :name="icon"
          :size="mobile ? 'sm' : 'lg'"
          :color="iconColor"
        />
      </q-card-section>

      <q-space v-if="mobile" />

      <q-card-section class="text-right">
        <b class="text-h6">{{ value }}</b>
        <br>
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
  computed: {
    mobile(): boolean {
      return this.$q.screen.lt.md;
    },
  },
  methods: {},
});

export default component;
</script>


<style lang="scss" scoped>
:deep(.q-card).compact {
  .q-card__section{
    padding-top: 8px;
    padding-bottom: 8px;
  }
}
</style>