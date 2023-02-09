<template>
  <!-- Modal -->
  <task-item-view
    v-model="children"
    @reload="$emit('reload')"
    @openParent="$emit('openParent', $event)"
    :root="root || children"
    :tree="genTree"
  ></task-item-view>

  <!-- Flat design -->
  <template v-if="flat">
    <template v-if="tasks?.length > 0">
      <task-item
        :modelValue="task"
        @update:modelValue="updateTask(task)"
        @updateItem="$emit('updateItem', $event)"
        @click="openChildren(task)"
        v-for="task of tasks"
        :key="task.id"
      ></task-item>
    </template>
    <template v-else>
      <h6 class="q-my-md">Нет категорий задач. Создайте новую ниже.</h6>
    </template>
  </template>

  <!-- Sorted design -->
  <template v-else>
    <!-- Uncompleted tasks -->
    <task-item
      :modelValue="task"
      @update:modelValue="updateTask(task)"
      @updateItem="$emit('updateItem', $event)"
      @click="openChildren(task)"
      v-for="task of tasksUnCompleted"
      :key="task.id"
    ></task-item>

    <!-- Add task item -->
    <q-item>
      <q-item-section avatar>
        <q-btn
          @click="createTask()"
          class="q-px-sm text-primary"
          icon="add_circle"
          rounded
          flat
        ></q-btn>
      </q-item-section>
      <q-item-section>
        <q-form @submit="createTask()">
          <q-input
            v-model="addTask"
            label="Добавить подзадачу"
            required
            outlined
            dense
          ></q-input>
        </q-form>
      </q-item-section>
    </q-item>

    <!-- Completed tasks -->
    <task-item
      :modelValue="task"
      @update:modelValue="updateTask(task)"
      @updateItem="$emit('updateItem', $event)"
      @click="openChildren(task)"
      v-for="task of tasksCompleted"
      :key="task.id"
    ></task-item>
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
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    taskItemView: defineAsyncComponent(() => import('./TaskItemView.vue')),
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    taskItem: taskItem,
  },
  props: {
    modelValue: { type: Array as PropType<TaskList> },
    root: { required: false, type: Object as PropType<TaskCategory> },
    tree: { required: false, type: Array as PropType<TaskList> },
    flat: { default: false, type: Boolean },
  },
  emits: ['updateItem', 'reload', 'openParent'],
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      children: false as Task | boolean,
      addTask: '' as string,
    };
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
      let parent = this.tree[this.tree.length - 1];

      let payload = {
        title: this.addTask,
        parent: isTaskCategory(parent) ? null : parent?.id,
        category: isTaskCategory(parent) ? parent.id : parent.category,
      };
      this.store
        .createTask(payload)
        .then(() => {
          this.loading = false;
          this.addTask = '';

          if (this.modelValue) {
            // let newItems = this.modelValue.slice();
            // newItems.push(resp.data);
            // this.$emit('update:modelValue', newItems);
          }

          this.$emit('reload');
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка создания категории');
        });
    },
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
});
</script>
