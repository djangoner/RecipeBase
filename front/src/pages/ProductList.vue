<template>
  <q-page>
    <week-select v-model="week" @update:modelValue="onWeekUpd()" />
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
        <q-select
          v-model="sortShop"
          label="Сортировка по магазину"
          :options="shops"
          style="width: 150px"
          option-label="title"
          option-value="id"
          map-options
          emit-value
          options-dense
          clearable
        ></q-select>
      </div>
      <div>
        <q-toggle v-model="showCompleted" label="Показать завершенные" />
      </div>
    </div>

    <!-- Product list -->
    <q-list class="row column q-col-gutter-y-md q-py-md q-px-none q-px-sm-lg">
      <!-- New item -->
      <div class="row items-center q-px-md">
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
      <!-- Prices total -->
      <span class="q-px-md q-pt-xs" v-if="pricesTotal"
        >{{ pricesCompleted }}₺ / {{ pricesTotal }}₺

        <q-tooltip>~ уже потрачено / стоимость продуктов</q-tooltip>
      </span>

      <!-- Product list item -->
      <template v-if="sortShop">
        <template v-for="cat of listItemsCategories" :key="cat.id">
          <div v-if="cat.items.length > 0">
            <div class="row q-mx-md">
              <h5
                class="q-my-sm"
                :class="categoryHasShop(cat) ? 'text-primary' : 'text-orange'"
              >
                {{ cat.title }}
                <q-tooltip v-if="cat.sortings">
                  <b>Магазины:</b>
                  <div v-for="sort of cat.sortings" :key="sort.id">
                    - {{ sort.shop.title }}
                  </div>
                  <div v-if="cat.sortings.length < 1">Нет магазинов</div>
                </q-tooltip>
              </h5>
            </div>

            <product-list-items
              :key="cat.id"
              :listItems="cat.items"
              :week="week"
              @openItem="openItem"
              @updateItem="updateItem"
            ></product-list-items>
          </div>
        </template>
      </template>
      <template v-else>
        <product-list-items
          :key="0"
          :listItems="listItems"
          :week="week"
          @openItem="openItem"
          @updateItem="updateItem"
        ></product-list-items>
      </template>
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

    let showCompleted = this.$q.localStorage.getItem('productsShowCompleted');
    if (showCompleted === null) {
      showCompleted = true;
    }

    return {
      store,
      loading: false,
      updating: false,
      saving: false,
      showCompleted: showCompleted,
      createItem: '',
      // week: {
      //   year: null,
      //   week: null,
      // },
      viewItem: null,
      canSyncFlag: false,
      WeekDays,
    };
  },
  mounted() {
    this.canSyncFlag = this.$q.localStorage.has('local_productlist_updated');

    if (this.isOnLine) {
      if (this.canSync) {
        this.$q.notify({
          type: 'info',
          caption: 'Рекомендуется выполнить синхронизацию изменений с сервером',
        });
      }
      this.loadShops();
      this.loadIngredientCategories();
      // if (this.$q.localStorage.has('local_productlist_updated')) {
      //   this.syncLocal();
      // }

      // this.loadList();
    } else {
      let local_cache = this.$q.localStorage.getItem('local_productlist');
      if (local_cache) {
        this.store.product_list = local_cache;
      }

      let shopsCache = this.$q.localStore.getItem('shops');
      if (shopsCache) {
        this.store.shops = shopsCache;
      }

      let ingCategoryCache = this.$q.localStore.getItem('ing_categories');
      if (ingCategoryCache) {
        this.store.ingredient_categories = ingCategoryCache;
      }
    }
  },
  methods: {
    onWeekUpd() {
      this.loadList();
      this.loadWeekPlan();
    },
    loadList() {
      if (!this.week?.year || !this.week?.week) {
        return;
      }
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
          let argTask = this.$query.task;
          if (!this.viewItem && argTask) {
            this.selectItemByID(argTask);
          }

          let rewriteLocal = !this.$q.localStorage.has('local_productlist_updated');
          if (rewriteLocal) {
            this.syncServer();
          }
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки списка продуктов');
        });
    },
    loadShops() {
      this.store
        .loadShops({ page_size: 1000 })
        .then((resp) => {
          this.$q.localStorage.set('shops', resp.data);
        })
        .catch((err) => {
          this.handleErrors('Ошибка загрузки списка магазинов');
          this.store.shops = this.$q.localStorage.getItem('shops', null);
        });
    },
    loadIngredientCategories() {
      this.store
        .loadIngredientCategories({ page_size: 1000 })
        .then((resp) => {
          this.$q.localStorage.set('ing_categories', resp.data);
        })
        .catch((err) => {
          this.handleErrors('Ошибка загрузки списка категорий ингредиентоа');
          this.store.shops = this.$q.localStorage.getItem('ing_categories', null);
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
    updateItem(item, reload) {
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
        this.syncServer();
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
          if (reload) {
            this.loadList();
          }
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
      // this.$query.task = item.id;
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
    selectItemByID(val) {
      let res = this.store.product_list?.items.filter((i) => i.id == val);
      this.viewItem = res[0];
    },
    loadWeekPlan() {
      if (!this.week?.year || !this.week?.week) {
        return;
      }
      let payload = {
        year: this.week.year,
        week: this.week.week,
      };
      this.loading = true;

      this.store
        .loadWeekPlan(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки плана');
        });
    },
    categoryHasShop(cat) {
      if (cat.custom) {
        return true;
      }
      if (!cat.sortings) {
        return;
      }
      return cat.sortings.find((s) => s.shop.id == this.sortShop);
    },
  },
  computed: {
    week: {
      get() {
        return { year: this.$query.year, week: this.$query.week };
      },
      set(val) {
        this.$query.year = val.year;
        this.$query.week = val.week;
      },
    },
    sortShop: {
      get() {
        return this.$query.shop || null;
      },
      set(val) {
        this.$query.shop = val;
      },
    },
    listItemsRaw() {
      return this.store.product_list?.items || [];
    },
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
    listItemsCategories: {
      get() {
        if (!this.ingredientCategories) {
          return [];
        }
        let categories = this.ingredientCategories.slice();

        categories.forEach((item, idx) => (categories[idx].items = [])); // Add items array
        categories = categories.reduce((obj, cur) => ({ ...obj, [cur.id]: cur }), {}); // Convert to object
        let items = this.listItems.slice();
        let itemsCompleted = items.filter((i) => i?.is_completed);
        items = items.filter((i) => itemsCompleted.indexOf(i) === -1);

        for (let [idx, item] of items.entries()) {
          let catItem = item?.ingredient?.category;
          if (!catItem) continue;
          let cat = categories[catItem?.id];
          if (!cat) continue;
          cat.items.push(Object.assign({}, item));
          delete items[idx];
        }

        categories[-1] = {
          title: 'Остальные',
          items: items.filter((i) => i).slice(),
          custom: true,
        };
        categories[-2] = {
          title: 'Завершенные',
          items: itemsCompleted,
          custom: true,
        };
        let categoriesList = [...Object.values(categories)];

        categoriesList.sort((a, b) => {
          if (a.custom) {
            return 1;
          } else if (b.custom) {
            return -1;
          }

          let aSort = a.sortings.find((s) => s?.shop?.id == this.sortShop);
          let bSort = b.sortings.find((s) => s?.shop?.id == this.sortShop);

          return aSort?.num - bSort?.num;
        });

        return categoriesList;
      },
      set(newValue) {
        if (this.store.product_list.items == newValue) {
          return;
        }
        this.store.product_list.items = newValue;
      },
    },
    shops() {
      return this.store.shops?.results;
    },
    ingredientCategories() {
      return this.store.ingredient_categories?.results;
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
    pricesCompleted() {
      return this.listItemsRaw
        .filter((i) => i.is_completed)
        .map((i) => i.price_full)
        .reduce((a, b) => a + b, 0);
    },
    pricesTotal() {
      return this.listItemsRaw.map((i) => i.price_full).reduce((a, b) => a + b, 0);
    },
  },
  watch: {
    viewItem: {
      get() {
        return this.$query.task;
      },
      set(val) {
        this.$query.task = val;
      },
    },
    showCompleted(val, oldVal) {
      this.$q.localStorage.set('productsShowCompleted', val);
    },
  },
};
</script>
