<template>
  <q-item clickable @click="$emit('click')">
    <q-item-section avatar v-if="task?.is_completed !== undefined">
      <q-checkbox
        v-model="task.is_completed"
        checked-icon="task_alt"
        unchecked-icon="radio_button_unchecked"
        @update:modelValue="$emit('updateItem', task)"
      />
    </q-item-section>
    <q-item-section avatar v-else>
      <q-icon :name="task?.icon || 'list'" />
    </q-item-section>

    <q-item-section>
      <q-item-label title>
        <template v-if="task.is_completed">
          <s class="text-grey">{{ task.title }}</s>
        </template>
        <template v-else>
          {{ task.title }}
        </template>
      </q-item-label>
      <q-item-label caption :lines="1">{{ task.description }}</q-item-label>
      <q-item-label caption v-if="task?.childrens?.length > 0">
        <q-icon name="account_tree" />
        {{ getCategoryCompleted(task) }} / {{ getCategoryAll(task) }}</q-item-label
      >
    </q-item-section>
  </q-item>
</template>

<script>
export default {
  props: { modelValue: { required: true } },
  methods: {
    getCategoryCompleted(category) {
      return category.childrens.filter((t) => t.is_completed).length;
    },
    getCategoryAll(category) {
      return category.childrens.length;
    },
  },
  computed: {
    task: {
      deep: true,
      get() {
        return this.modelValue;
      },
      set(val) {
        this.$emit('update:modelValue'), val;
      },
    },
  },
};
</script>
