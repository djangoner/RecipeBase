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
    <task-item
      :modelValue="task"
      @update:modelValue="updateTask(task)"
      @updateItem="$emit('updateItem', $event)"
      @click="openChildren(task)"
      v-for="task of tasks"
      :key="task.id"
    ></task-item>
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

<script>
import { defineAsyncComponent } from 'vue-demi';
// import taskItemView from 'components/TaskItemView.vue';
import taskItem from 'components/TaskItem.vue';
import { useBaseStore } from 'src/stores/base';

export default {
  components: {
    taskItemView: defineAsyncComponent(() => import('./TaskItemView.vue')),
    taskItem,
  },
  props: {
    modelValue: Array,
    root: { required: false },
    tree: { required: false },
    flat: { default: false },
  },
  emits: ['updateItem', 'reload', 'openParent'],
  data() {
    const store = useBaseStore();
    return {
      store,
      children: false,
      addTask: '',
    };
  },
  methods: {
    updateItem(task) {
      console.debug('Update task', task);
      this.$emit('updateItem', task);
    },
    openChildren(task) {
      this.children = task;
    },
    updateTask(task) {
      this.$emit('updateItem', task);
      this.childrens = this.childrens.map((c) => {
        if (c.id == task.id) {
          return task;
        }
        return c;
      });
    },
    createTask() {
      if (!this.addTask) {
        return;
      }
      this.loading = true;
      let parent = this.tree[this.tree.length - 1];

      let payload = {
        title: this.addTask,
        parent: parent?.id,
        category: parent?.category || parent?.id,
      };
      this.store
        .createTask(payload)
        .then((resp) => {
          this.loading = false;
          this.addTask = '';

          if (this.modelValue) {
            // let newItems = this.modelValue.slice();
            // newItems.push(resp.data);
            // this.$emit('update:modelValue', newItems);
          }

          this.$emit('reload');
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка создания категории');
        });
    },
  },
  computed: {
    tasks() {
      return this.modelValue || [];
    },
    genTree() {
      let tree;
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
    tasksUnCompleted() {
      return this.tasks.filter((t) => !t.is_completed);
    },
    tasksCompleted() {
      return this.tasks.filter((t) => t.is_completed);
    },
  },
  watch: {
    modelValue: {
      deep: true,
      handler(val, oldVal) {
        console.debug('Updating tree');
        this.children = this.tasks.find((t) => t.id == this.children?.id);
      },
    },
  },
};
</script>
