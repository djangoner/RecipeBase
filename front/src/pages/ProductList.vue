<template>
  <q-page>
    <week-select v-model="week" @update:modelValue="loadList()" />
    <q-linear-progress v-show="saving" indeterminate />
    <product-list-item-view v-model="viewItem" :week="week" @updateItem="updateItem" />

    <div class="row items-center q-mt-sm q-ml-md">
      <q-btn
        label="Обновить автоматический список"
        color="primary"
        icon="refresh"
        size="sm"
        @click="regenerateList()"
      ></q-btn>
      <q-toggle v-model="showCompleted" label="Показать завершенные" />
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

    <q-inner-loading :showing="loading || saving"></q-inner-loading>
  </q-page>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
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
      WeekDays,
    };
  },
  mounted() {
    let [year, week] = getWeekNumber(new Date());
    this.week.year = year;
    this.week.week = week;
    this.loadList();
  },
  beforeRouteUpdate(to) {},
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
    updateItem(item) {
      let payload = Object.assign({}, item);

      delete payload['ingredient'];
      delete payload['ingredients'];

      this.saving = true;

      this.store
        .updateProductListItem(payload)
        .then((resp) => {
          this.store.product_list.items = this.store.product_list.items.map((i) => {
            if (i.id == item.id) {
              console.debug(resp);
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
        console.debug('set: ', newValue, this.store.product_list.items);
        if (this.store.product_list.items == newValue) {
          return;
        }
        // this.store.product_list.items = newValue;
      },
    },
  },
  watch: {
    // viewItem(val) {
    //   this.$router.replace({ query: { task: val?.id } });
    // },
  },
};
</script>
