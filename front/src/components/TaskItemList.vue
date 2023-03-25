<template>
  <!-- Modal -->
  <task-item-view
    v-model="children"
    :can-edit="canEdit"
    :root="root || children"
    :tree="genTree"
    @reload="$emit('reload')"
    @open-parent="$emit('openParent', $event)"
  />

  <!-- Flat design -->
  <template v-if="flat">
    <template v-if="tasks?.length > 0">
      <task-item
        v-for="task of tasks"
        :key="task.id"
        :model-value="task"
        @update:model-value="updateTask(task)"
        @update-item="$emit('updateItem', $event)"
        @click="openChildren(task)"
      />
    </template>
    <template v-else>
      <h6 class="q-my-md">
        Нет категорий задач. Создайте новую ниже.
      </h6>
    </template>
  </template>

  <!-- Sorted design -->
  <template v-else>
    <!-- Uncompleted tasks -->
    <task-item
      v-for="task of tasksUnCompleted"
      :key="task.id"
      :model-value="task"
      :can-edit="canEdit"
      @update:model-value="updateTask(task)"
      @update-item="$emit('updateItem', $event)"
      @click="openChildren(task)"
    />

    <!-- Add task item -->
    <q-item v-if="canEdit">
      <q-item-section avatar>
        <q-btn
          class="q-px-sm text-primary"
          icon="add_circle"
          rounded
          flat
          @click="createTask()"
        />
      </q-item-section>
      <q-item-section>
        <q-form @submit="createTask()">
          <q-input
            v-model="addTask"
            label="Добавить подзадачу"
            required
            outlined
            dense
          />
        </q-form>
      </q-item-section>
    </q-item>

    <!-- Completed tasks -->
    <task-item
      v-for="task of tasksCompleted"
      :key="task.id"
      :model-value="task"
      :can-edit="canEdit"
      @update:model-value="updateTask(task)"
      @update-item="$emit('updateItem', $event)"
      @click="openChildren(task)"
    />
  </template>
</template>

<script lang="ts">
import { defineAsyncComponent, defineComponent, PropType } from 'vue';
// import taskItemView from 'components/TaskItemView.vue';
import taskItem from 'components/TaskItem.vue';
import { useBaseStore } from 'src/stores/base';
import { Task, TaskCategory } from 'src/client';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { isTaskCategory } from 'src/modules/Utils';
import { TaskOrCategory } from 'src/modules/Globals';

type TaskList = TaskOrCategory[];

export default defineComponent({
  name: 'TaskItemList',
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    taskItemView:defineAsyncComponent(() => import('./TaskItemView.vue')),
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    taskItem: taskItem,
  },
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: { type: Array as PropType<TaskOrCategory[]>, required: true },
    root: { required: false, default: null, type: Object as PropType<TaskCategory> },
    tree: { required: false, default: null, type: Array as PropType<TaskList> },
    flat: { default: false, type: Boolean },
    canEdit: { default: true, type: Boolean },
    isCategory: { default: false, type: Boolean },
  },
  emits: ['updateItem', 'reload', 'openParent'],
  data() {
    const store = useBaseStore();
    return {
      store,
      children: false as TaskOrCategory | boolean,
      addTask: '' as string,
      loading: false,
    };
  },
  computed: {
    tasks() {
      return this.modelValue || [];
    },
    genTree(): TaskList {
      let tree: TaskList;
      if (this.tree) {
        tree = this.tree.slice();
      } else {
        tree = [];
      }

      if (this.children) {
        return [...tree, this.children];
      } else {
        return tree;
      }
    },
    isTaskCategory(){
      return this.isCategory
    },
    tasksUnCompleted(): TaskList {
      return this.tasks.filter((t) => !t.is_completed);
    },
    tasksCompleted(): TaskList {
      return this.tasks.filter((t) => t.is_completed);
    },
  },
  watch: {
    modelValue: {
      deep: true,
      handler() {
        console.debug('Updating tree');
        this.children = this.tasks.find((t) => t.id == this.children?.id);
      },
    },
  },
  methods: {
    updateItem(task: Task) {
      console.debug('Update task', task);
      this.$emit('updateItem', task);
    },
    openChildren(task: Task) {
      this.children = task;
    },
    updateTask(task: Task) {
      this.$emit('updateItem', task);
      // this.childrens = this.childrens.map((c) => {
      //   if (c.id == task.id) {
      //     return task;
      //   }
      //   return c;
      // });
    },
    createTask() {
      if (!this.addTask) {
        return;
      }
      this.loading = true;
      const parent = this.tree[this.tree.length - 1];

      const payload = {
        title: this.addTask,
        parent: isTaskCategory(parent) ? null : parent?.id,
        category: isTaskCategory(parent) ? parent.id : parent.category,
      };
      this.store
      // @ts-expect-error new task
        .createTask(payload)
        .then(() => {
          this.loading = false;
          this.addTask = '';

          if (this.modelValue) {
            // let newItems = this.modelValue.slice();
            // newItems.push(resp.data);
            // this.$emit('update:model-value', newItems);
          }

          this.$emit('reload');
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка создания категории');
        });
    },
  },
});
</script>
