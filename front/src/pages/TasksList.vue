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

<script>
import { useBaseStore } from 'src/stores/base';
// import taskCategoryView from 'src/components/TaskItemView.vue';
import taskItemList from 'components/TaskItemList.vue';

export default {
  components: { taskItemList },
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      category: null,
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
        .then((resp) => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка списка категорий задач');
        });
    },

    getCategoryCompleted(category) {
      return category.childrens.filter((t) => t.is_completed).length;
    },
    getCategoryAll(category) {
      return category.childrens.length;
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
        .createTaskCategory(payload)
        .then((resp) => {
          this.loading = false;
          this.addCategory = '';
          this.loadTaskCategories();
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузка создания категории');
        });
    },
    openCategory(category) {
      this.category = category;
    },
  },

  computed: {
    taskCategories() {
      return this.store.tasks_categories?.results;
    },
  },
};
</script>
