<template>
  <q-page padding>
    <q-list v-if="taskCategories">
      <task-item-list
        v-model="taskCategories"
        :flat="true"
        @reload="loadTaskCategories()"
      ></task-item-list>

      <q-form @submit.prevent="createCategory()">
        <q-item class="q-mt-lg">
          <q-item-section avatar>
            <q-btn
              type="submit"
              icon="add"
              color="green"
              flat
              round
              dense
              no-caps
            ></q-btn>
          </q-item-section>
          <q-item-section>
            <q-input
              v-model="addCategory"
              label="Создать категорию"
              required
              outlined
              dense
            >
            </q-input>
          </q-item-section>
        </q-item>
      </q-form>
    </q-list>

    <q-inner-loading :showing="loading" />
  </q-page>
</template>

<script lang="ts">
import { useBaseStore } from 'src/stores/base';
// import taskCategoryView from 'src/components/TaskItemView.vue';
import taskItemList from 'components/TaskItemList.vue';
import { defineComponent } from 'vue';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { TaskOrCategory } from 'src/modules/Globals';

export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { taskItemList },
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      category: null as TaskOrCategory | null,
      addCategory: '',
    };
  },

  mounted() {
    this.loadTaskCategories();
  },

  methods: {
    loadTaskCategories() {
      let payload = {
        page_size: 1000,
      };
      this.loading = true;
      this.store
        .loadTaskCategories(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка списка категорий задач');
        });
    },

    createCategory() {
      if (!this.addCategory) {
        return;
      }
      this.loading = true;
      let payload = {
        title: this.addCategory,
      };
      this.store
        // @ts-expect-error: Task will be created
        .createTaskCategory(payload)
        .then(() => {
          this.loading = false;
          this.addCategory = '';
          this.loadTaskCategories();
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка создания категории');
        });
    },
    openCategory(category: TaskOrCategory) {
      this.category = category;
    },
  },

  computed: {
    taskCategories() {
      return this.store.tasks_categories;
    },
  },
});
</script>
