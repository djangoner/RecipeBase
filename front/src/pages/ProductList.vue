<template>
  <q-page>
    <week-select v-model="week" @update:modelValue="loadList()" />
    <q-linear-progress
      :value="completedPrc"
      :indeterminate="saving"
      :instant-feedback="saving"
      :animation-speed="500"
    />
    <product-list-item-view v-model="viewItem" :week="week" @updateItem="updateItem" />

    <div class="row items-center q-mt-sm q-ml-sm q-col-gutter-sm">
      <div>
        <q-btn
          label="Обновить автоматический список"
          class="q-ml-none"
          color="primary"
          icon="refresh"
          size="sm"
          @click="regenerateList()"
          :disable="!isOnLine"
        ></q-btn>
      </div>
      <div>
        <q-btn
          label="Синхронизация"
          :color="canSync ? 'positive' : 'primary'"
          icon="sync"
          size="sm"
          @click="syncLocal()"
          :disable="!canSync"
        >
          <q-tooltip v-if="!canSync">Нет данных для синхронизации</q-tooltip>
        </q-btn>
      </div>
      <div>
        <q-toggle v-model="showCompleted" label="Показать завершенные" />
      </div>
    </div>

    <!-- Product list -->
    <q-list class="row column q-col-gutter-y-md q-py-md q-px-none q-px-sm-lg">
      <!-- New item -->
      <div class="row items-center q-px-md q-mb-md">
        <div class="col-grow">
          <q-input
            v-model="createItem"
            label="Добавить задачу"
            @keypress.enter="createNewItem()"
          ></q-input>
        </div>
        <q-btn
          class="col-auto q-ml-md"
          icon="add"
          size="sm"
          color="green"
          dense
          @click="createNewItem()"
        >
        </q-btn>
      </div>

      <!-- Product list item -->
      <product-list-items
        v-model="listItems"
        :week="week"
        @openItem="openItem"
        @updateItem="updateItem"
      ></product-list-items>
    </q-list>

    <q-inner-loading :showing="loading"></q-inner-loading>
  </q-page>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
  getYearWeek,
} from 'components/WeekSelect.vue';
import ProductListItemView from 'components/ProductListItemView.vue';
import ProductListItems from 'components/ProductListItems.vue';

export default {
  components: {
    weekSelect,
    ProductListItemView,
    ProductListItems,
  },
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      updating: false,
      saving: false,
      showCompleted: true,
      createItem: '',
      week: {
        year: null,
        week: null,
      },
      viewItem: null,
      canSyncFlag: false,
      WeekDays,
    };
  },
  mounted() {
    let [year, week] = getYearWeek();
    this.week.year = year;
    this.week.week = week;

    this.canSyncFlag = this.$q.localStorage.has('local_productlist_updated');

    if (this.isOnLine) {
      if (this.canSync) {
        this.$q.notify({
          type: 'info',
          caption: 'Рекомендуется выполнить синхронизацию изменений с сервером',
        });
      }
      // if (this.$q.localStorage.has('local_productlist_updated')) {
      //   this.syncLocal();
      // }
      this.loadList();
    } else {
      let local_cache = this.$q.localStorage.getItem('local_productlist');
      if (local_cache) {
        this.store.product_list = local_cache;
      }
    }
  },
  beforeRouteUpdate(to) {
    this.loadList();
  },
  methods: {
    loadList() {
      let payload = {
        year: this.week.year,
        week: this.week.week,
        page_size: 1000,
      };
      this.loading = true;

      this.store
        .loadProductListWeek(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки списка продуктов');
        });
    },
    syncServer() {
      console.debug('SyncServer');
      this.$q.localStorage.set('local_productlist', this.store?.product_list);

      if (!this.isOnLine) {
        this.$q.localStorage.set('local_productlist_updated', true);
      }
    },
    syncLocal() {
      this.$q.notify({
        type: 'info',
        caption: 'Синхронизация изменений с сервером...',
        icon: 'cloud_sync',
      });

      this.loading = true;

      let payload = this.$q.localStorage.getItem('local_productlist');
      payload.items = payload.items.map((item) => {
        delete item['ingredient'];
        delete item['ingredients'];
        return item;
      });
      console.debug('SyncLocal: ', payload);

      this.store
        .saveProductListWeek(payload)
        .then(() => {
          this.loading = false;
          this.$q.notify({
            type: 'positive',
            caption: 'Список продуктов успешно синхронизирован',
          });
          this.$q.localStorage.remove('local_productlist_updated');
          this.canSync = false;

          // this.loadList();
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка синхронизации списка продуктов');
        });
    },
    updateItem(item) {
      if (!item) {
        return;
      }
      if (!this.isOnLine) {
        console.debug('Upd item: ', item);
        // Update offline data
        this.store.product_list.items = this.store.product_list.items.map((i) => {
          if (i.id == item.id) {
            // console.debug(resp);
            return item;
          }
          return i;
        });
        // this.syncServer();
        return;
      }
      let payload = Object.assign({}, item);

      delete payload['ingredient'];
      delete payload['ingredients'];

      this.saving = true;

      this.store
        .updateProductListItem(payload)
        .then((resp) => {
          this.store.product_list.items = this.store.product_list.items.map((i) => {
            if (i.id == item.id) {
              // console.debug(resp);
              return resp.data;
            }
            return i;
          });
          this.saving = false;
        })
        .catch((err) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка сохранения списка продуктов');
        });
    },
    deleteItem(item) {},
    regenerateList() {
      let payload = {
        year: this.week.year,
        week: this.week.week,
        page_size: 1000,
      };
      this.loading = true;

      this.store
        .generateProductListWeek(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка обновления списка продуктов');
        });
    },
    openItem(item) {
      console.debug('Open item: ', item);
      this.viewItem = item;
    },
    createNewItem() {
      let payload = {
        title: this.createItem,
        week: this.store.product_list.id,
      };
      this.createItem = '';

      this.saving = true;
      this.store
        .createProductListItem(payload)
        .then((resp) => {
          this.saving = false;
          this.viewItem = resp.data;
          this.store.product_list.items.push(resp.data);
        })
        .catch((err) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка создания задачи');
        });
    },
  },
  computed: {
    listItems: {
      get() {
        let res = this.store.product_list?.items || [];
        res = res.slice();

        if (res) {
          if (!this.showCompleted) {
            res = res.filter((i) => !i.is_completed);
          }
          res.sort((a, b) => {
            if (a.is_completed) {
              return 1;
            } else if (b.is_completed) {
              return -1;
            }
            return a.day - b.day;
          });
        }
        return res;
      },
      set(newValue) {
        // console.debug('set: ', newValue, this.store.product_list.items);
        if (this.store.product_list.items == newValue) {
          return;
        }
        // this.store.product_list.items = newValue;
      },
    },
    completedPrc() {
      let itemsCompleted = this.store.product_list?.items.filter((i) => i.is_completed)
        ?.length;
      let itemsTotal = this.store.product_list?.items?.length;

      if (!itemsCompleted || !itemsTotal) {
        return 0;
      }
      return itemsCompleted / itemsTotal;
    },
    canSync: {
      get() {
        return this.isOnLine && this.canSyncFlag;
      },
      set(val) {
        this.canSyncFlag = val;
      },
    },
  },
  watch: {
    isOnLine(val, oldVal) {
      if (val && !oldVal) {
        this.canSyncFlag = this.$q.localStorage.has('local_productlist_updated');
      } else if (!val && oldVal) {
        this.canSyncFlag = false;
      }
    },
    listItems(val, oldVal) {
      if (val !== oldVal) {
        this.syncServer();
      }
    },
    // viewItem(val) {
    //   this.$router.replace({ query: { task: val?.id } });
    // },
  },
};
</script>
