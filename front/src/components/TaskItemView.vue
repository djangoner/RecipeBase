<template>
  <q-dialog
    :model-value="!!modelValue"
    @update:modelValue="setOpened"
    :no-backdrop-dismiss="$q.screen.gt.md"
  >
    <q-card style="width: 700px; max-width: 95vw; height: 80vh">
      <q-linear-progress :indeterminate="saving" :instant-feedback="true" />

      <!-- Top row -->
      <q-card-section class="row items-center no-wrap q-pb-none" v-if="category">
        <q-checkbox
          v-if="category?.is_completed !== undefined"
          v-model="category.is_completed"
          checked-icon="task_alt"
          unchecked-icon="radio_button_unchecked"
          indeterminate-icon="help"
          size="lg"
          @update:modelValue="updateItem()"
        />
        <q-input
          v-model="category.title"
          @update:modelValue="updateItem()"
          class="col"
          :debounce="500"
          dense
        />
        <q-space />
        <!-- Actions menu -->
        <q-btn class="q-ml-sm q-mr-md" icon="menu" size="sm" round flat>
          <q-menu anchor="bottom right" self="top right">
            <q-list dense>
              <q-item>
                <q-item-section>
                  <q-item-label caption
                    >Добавлено {{ dateFormat(category.created) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item
                @click="askDeleteTask()"
                class="text-negative"
                clickable
                v-close-popup
              >
                <q-item-section avatar><q-icon name="delete" size="xs" /></q-item-section>
                <q-item-section>Удалить</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        <q-btn icon="close" flat round dense v-close-popup></q-btn>
      </q-card-section>

      <!-- Breadcrumbs -->
      <q-card-section v-if="tree.length > 1">
        <q-separator />
        <q-breadcrumbs class="q-my-sm cursor-pointer">
          <template v-slot:separator>
            <q-icon size="1.5em" name="chevron_right" color="primary" />
          </template>

          <q-breadcrumbs-el
            @click="openParent(task)"
            v-for="task in tree"
            :key="task.id"
            :label="task.title"
          ></q-breadcrumbs-el>
        </q-breadcrumbs>
        <q-separator />
      </q-card-section>

      <!-- Content -->
      <q-card-section class="q-pt-none">
        <q-input
          v-model="category.description"
          @update:modelValue="updateItem()"
          :debounce="2000"
          type="textarea"
          label="Описание задачи"
          autogrow
          input-style="max-height: 5rem;"
        >
          <template #prepend>
            <q-icon name="notes" size="sm" />
          </template>
        </q-input>

        <q-expansion-item
          v-model="expanded"
          class="q-mt-sm"
          header-class="q-pl-sm"
          switch-toggle-side
          dense
          dense-toggle
        >
          <template #header>
            <div class="row items-center justify-between col-grow">
              <div class="text-subtitle2 text-grey-8">
                Подзадачи
                <small class="text-grey">
                  {{ getCategoryCompleted(category) }} /
                  {{ getCategoryAll(category) }}
                </small>
              </div>

              <q-space />
            </div>
          </template>

          <q-list>
            <task-item-list
              v-model="category.childrens"
              @updateItem="updateItem"
              @reload="$emit('reload')"
              @openParent="openParent"
              :root="root"
              :tree="tree"
            >
            </task-item-list>
          </q-list>
        </q-expansion-item>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script>
import taskItemList from 'src/components/TaskItemList.vue';
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';

export default {
  components: { taskItemList },
  props: {
    modelValue: { required: true },
    root: { required: false },
    tree: { required: false },
  },
  emits: ['reload', 'openParent'],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      saving: false,
      expanded: true,
    };
  },
  methods: {
    setOpened(val) {
      this.$emit('update:modelValue', val || null);
    },
    updateItem(item) {
      let useThis = false;
      if (!item) {
        item = this.category;
        useThis = true;
      }
      console.debug('Update item', item);
      this.saving = true;

      let method =
        item?.is_completed !== undefined
          ? this.store.updateTask
          : this.store.updateTaskCategory;

      let updateData = Object.assign({}, item);
      if (updateData?.childrens) {
        delete updateData['childrens'];
      }

      method(updateData)
        .then((resp) => {
          this.saving = false;
          if (useThis) {
            this.category = resp.data;
          } else {
            item = resp.data;
          }
        })
        .catch((err) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка сохранения задачи');
        });
    },
    getCategoryCompleted(category) {
      return category?.childrens?.filter((t) => t.is_completed)?.length;
    },
    getCategoryAll(category) {
      return category?.childrens?.length;
    },
    openParent(target) {
      console.debug('openParent', target, this.category);
      if (target?.id == this.category?.id && target?.title == this.category?.title) {
        return;
      } else {
        console.debug('Close');
        this.setOpened(null);
      }
      this.$emit('openParent', target);
    },

    deleteTask(item) {
      if (!item) {
        item = this.category;
      }
      let method =
        item?.is_completed !== undefined
          ? this.store.deleteTask
          : this.store.deleteTaskCategory;

      this.saving = true;
      method(item)
        .then((resp) => {
          this.saving = false;
          this.setOpened(null);
          this.$emit('reload');
        })
        .catch((err) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка удаления задачи');
        });
    },
    askDeleteTask() {
      this.$q
        .dialog({
          title: 'Подтверждение',
          message: 'Вы уверены что хотите удалить эту задачу?',
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.deleteTask();
        });
    },
    dateFormat(raw) {
      return date.formatDate(raw, 'YYYY.MM.DD hh:mm');
    },
  },
  computed: {
    category() {
      return this.modelValue;
    },
  },
};
</script>
