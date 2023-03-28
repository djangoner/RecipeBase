<template>
  <q-item
    clickable
    @click="$emit('click')"
  >
    <q-item-section
      v-if="task?.is_completed !== undefined"
      avatar
    >
      <q-checkbox
        v-model="task.is_completed"
        checked-icon="task_alt"
        unchecked-icon="radio_button_unchecked"
        :disable="!canEdit"
        @update:model-value="$emit('updateItem', task)"
      />
    </q-item-section>
    <q-item-section
      v-else
      avatar
    >
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
      <q-item-label
        caption
        :lines="1"
      >
        {{ task.description }}
      </q-item-label>
      <q-item-label
        v-if="task?.childrens?.length > 0"
        caption
      >
        <q-icon name="account_tree" />
        {{ getCategoryCompleted(task) }} / {{ getCategoryAll(task) }}
      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script lang="ts">
import { TaskCategoryCountAll, TaskCategoryCountCompleted } from 'src/modules/Utils';
import { defineComponent, PropType } from 'vue';
import {Task} from 'src/client'

export default defineComponent({
  props: { modelValue: { type: Object as PropType<Task>,required: true }, canEdit: { default: true, type: Boolean } },
  emits: ['update:model-value','click', 'updateItem'],
  computed: {
    task: {
      deep: true,
      get() {
        return this.modelValue;
      },
      set(val: Task) {
        this.$emit('update:model-value'), val;
      },
    },
  },
  methods: {
    getCategoryCompleted: TaskCategoryCountCompleted,
    getCategoryAll: TaskCategoryCountAll,
  },
});
</script>
