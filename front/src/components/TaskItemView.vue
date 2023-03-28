<template>
  <q-dialog
    :model-value="!!modelValue"
    @update:model-value="setOpened"
  >
    <q-card style="width: 700px; max-width: 95vw; height: 80vh">
      <q-linear-progress
        :indeterminate="saving"
        :instant-feedback="true"
      />

      <!-- Top row -->
      <q-card-section
        v-if="category"
        class="row items-center no-wrap q-pb-none"
      >
        <q-checkbox
          v-if="category?.is_completed !== undefined"
          v-model="category.is_completed"
          :disable="!canEdit"
          checked-icon="task_alt"
          unchecked-icon="radio_button_unchecked"
          indeterminate-icon="help"
          size="lg"
          @update:model-value="updateItem()"
        />
        <q-input
          v-model="category.title"
          :readonly="!canEdit"
          class="col"
          :debounce="500"
          dense
          @update:model-value="updateItem()"
        />
        <q-space />
        <!-- Actions menu -->
        <q-btn
          class="q-ml-sm q-mr-md"
          icon="menu"
          size="sm"
          round
          flat
        >
          <q-menu
            anchor="bottom right"
            self="top right"
          >
            <q-list dense>
              <q-item>
                <q-item-section>
                  <q-item-label caption>
                    Добавлено {{ dateFormat(category.created) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item
                v-if="canEdit"
                v-close-popup
                class="text-negative"
                clickable
                @click="askDeleteTask()"
              >
                <q-item-section avatar>
                  <q-icon
                    name="delete"
                    size="xs"
                  />
                </q-item-section>
                <q-item-section>Удалить</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        <q-btn
          v-close-popup
          icon="close"
          flat
          round
          dense
        />
      </q-card-section>

      <!-- Breadcrumbs -->
      <q-card-section v-if="tree.length > 1">
        <q-separator />
        <q-breadcrumbs class="q-my-sm cursor-pointer">
          <template #separator>
            <q-icon
              size="1.5em"
              name="chevron_right"
              color="primary"
            />
          </template>

          <q-breadcrumbs-el
            v-for="task in tree"
            :key="task.id"
            :label="task.title"
            @click="openParent(task)"
          />
        </q-breadcrumbs>
        <q-separator />
      </q-card-section>

      <!-- Content -->
      <q-card-section class="q-pt-none">
        <q-input
          v-model="category.description"
          :debounce="2000"
          :readonly="!canEdit"
          type="textarea"
          label="Описание задачи"
          autogrow
          input-style="max-height: 5rem;"
          @update:model-value="updateItem()"
        >
          <template #prepend>
            <q-icon
              name="notes"
              size="sm"
            />
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
              :can-edit="canEdit"
              :root="root"
              :tree="tree"
              @update-item="updateItem"
              @reload="$emit('reload')"
              @open-parent="openParent"
            />
          </q-list>
        </q-expansion-item>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script lang="ts">
// import taskItemList from 'src/components/TaskItemList.vue';
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';
import { defineAsyncComponent, defineComponent, PropType } from 'vue';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import {
  isTaskCategory,
  TaskCategoryCountAll,
  TaskCategoryCountCompleted,
} from 'src/modules/Utils';
import { TaskOrCategory } from 'src/modules/Globals';
import { Task, TaskCategory } from 'src/client';

type TaskList = TaskOrCategory[];

export default defineComponent({
  name: 'TaskItemView',
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { taskItemList:defineAsyncComponent(() => import('./TaskItemList.vue')) },
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: { required: true, type: Object as PropType<Task> },
    root: { required: false, default: null, type: Object as PropType<TaskCategory> },
    tree: { required: false, default: null, type: Array as PropType<TaskList>},
    canEdit: { required: true, type: Boolean },
  },
  emits: ['reload', 'openParent', 'update:model-value'],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      saving: false,
      expanded: true,
    };
  },
  computed: {
    isTaskCategory,
    category(): Task | TaskCategory {
      return this.modelValue;
    },
  },
  methods: {
    getCategoryCompleted: TaskCategoryCountCompleted,
    getCategoryAll: TaskCategoryCountAll,
    setOpened(val?: boolean | null) {
      this.$emit('update:model-value', val || null);
    },
    updateItem(item?: TaskOrCategory) {
      let useThis = false;
      if (!item) {
        item = this.category;
        useThis = true;
      }
      console.debug('Update item', item);
      this.saving = true;

      const method = isTaskCategory(item)
        ? this.store.updateTaskCategory
        : this.store.updateTask;

      const updateData = Object.assign({}, item);
      if (updateData?.childrens) {
        // @ts-expect-error don't update childrens
        delete updateData['childrens'];
      }

      // @ts-expect-error Custom update
      method(updateData)
        .then((resp) => {
          this.saving = false;
          if (useThis) {
            this.category = resp;
          } else {
            item = resp;
          }
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка сохранения задачи');
        });
    },
    openParent(target: TaskOrCategory) {
      console.debug('openParent', target, this.category);
      if (target?.id == this.category?.id && target?.title == this.category?.title) {
        return;
      } else {
        console.debug('Close');
        this.setOpened(null);
      }
      this.$emit('openParent', target);
    },

    deleteTask(item?: TaskOrCategory | undefined) {
      if (!item) {
        item = this.category;
      }
      const method = isTaskCategory(item)
        ? this.store.deleteTaskCategory
        : this.store.deleteTask;

      this.saving = true;
      method(item.id)
        .then(() => {
          this.saving = false;
          this.setOpened(null);
          this.$emit('reload');
        })
        .catch((err: CustomAxiosError) => {
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
    dateFormat(raw: Date): string {
      return date.formatDate(raw, 'YYYY.MM.DD hh:mm');
    },
  },
});
</script>
