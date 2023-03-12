<template>
  <q-page>
    <!-- Top bar -->
    <week-select v-model="week" @update:modelValue="onWeekUpd()" />
    <q-linear-progress
      :value="completedPrc"
      :indeterminate="saving"
      :instant-feedback="saving"
      :animation-speed="500"
    />
    <!-- Top warnings -->
    <q-item v-if="markAlreadyCompleted" class="bg-info text-white">
      <q-item-section avatar><q-icon name="info"></q-icon></q-item-section>
      <q-item-section>Режим "отметить что уже есть"</q-item-section>
    </q-item>
    <!-- Modals -->
    <product-list-item-view
      v-model="viewItem"
      :week="week"
      :canEdit="canEdit"
      @updateItem="updateItem"
    />
    <!-- Contents -->

    <div
      class="row items-center q-mt-sm q-ml-sm q-col-gutter-sm q-mr-md no-wrap"
      :class="$q.screen.lt.md ? 'justify-between' : ''"
    >
      <div>
        <q-select
          v-model="sortShop"
          label="Группировать"
          :options="shops || []"
          style="width: 120px"
          option-label="title"
          option-value="id"
          map-options
          emit-value
          options-dense
          clearable
          dense
        ></q-select>
      </div>
      <div>
        <q-toggle v-model="showCompleted" label="Показать завершенные" dense />
      </div>

      <q-space />
      <div>
        <q-btn icon="menu" size="md" flat round dense>
          <q-menu>
            <q-list dense>
              <q-item tag="label" v-ripple>
                <q-item-section side>
                  <q-toggle v-model="markAlreadyCompleted" dense />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Отметить что уже есть</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                v-if="storeAuth.hasPerm('recipes.change_productlistitem')"
                @click="regenerateList()"
                :disable="!isOnLine"
                clickable
              >
                <q-item-section avatar>
                  <q-icon name="refresh" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label> Обновить автоматический список </q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="storeAuth.hasPerm('recipes.change_productlistitem')"
                @click="askSyncLocal()"
                :disable="!canSync"
                clickable
              >
                <q-item-section avatar>
                  <q-icon name="sync" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label> Синхронизация </q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="canSync"
                @click="askDiscardSync()"
                :disable="!canSync"
                clickable
              >
                <q-item-section avatar>
                  <q-icon name="delete" color="negative" />
                </q-item-section>
                <q-item-section>
                  <q-item-label> Очистка синхронизации </q-item-label>
                </q-item-section>
              </q-item>

              <q-item clickable v-close-popup @click="sendList()">
                <q-item-section avatar><q-icon name="send" /> </q-item-section>
                <q-item-section>
                  <q-item-label> Отправить в телеграмм </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </div>
    </div>

    <!-- Product list -->
    <q-list class="row column q-col-gutter-y-md q-py-md q-px-none q-px-sm-lg">
      <!-- New item -->
      <div class="row items-center q-px-md">
        <div class="col-grow">
          <q-input
            v-if="storeAuth.hasPerm('recipes.add_productlistitem')"
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
      <span class="q-px-md q-pt-xs">
        {{ pricesCompleted }}₺ / {{ pricesTotal }}₺
        <template v-if="productsWithoutPrice">
          ({{ productsWithoutPrice }}/{{ listItemsRaw.length }} продуктов без
          цены)
        </template>

        <q-tooltip>~ уже потрачено / стоимость продуктов</q-tooltip>
      </span>

      <!-- Product list item -->
      <template v-if="sortShop">
        <template v-for="cat of listItemsCategories">
          <div v-if="cat.items && cat.items.length > 0" :key="cat.id">
            <div class="row q-mx-md">
              <h5
                class="q-my-sm"
                :class="categoryHasShop(cat) ? 'text-primary' : 'text-orange'"
              >
                {{ cat.title }}
                <q-tooltip v-if="cat.sorting">
                  <b>Магазины:</b>
                  <div v-for="sort of cat.sorting" :key="sort.id">
                    - {{ sort.shop.title }}
                  </div>
                  <div v-if="cat.sorting.length < 1">Нет магазинов</div>
                </q-tooltip>
              </h5>
            </div>

            <product-list-items
              :key="cat.id"
              :listItems="cat.items"
              :week="week"
              :canEdit="canEdit"
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
          :canEdit="canEdit"
          @openItem="openItem"
          @updateItem="updateItem"
        ></product-list-items>
      </template>
    </q-list>

    <q-inner-loading :showing="loading"></q-inner-loading>
  </q-page>
</template>

<script lang="ts">
import ProductListItems from "components/ProductListItems.vue";
import ProductListItemView from "components/ProductListItemView.vue";
import weekSelect from "components/WeekSelect.vue";
import {
  IngredientCategory,
  ProductListItemRead,
  ProductListWeekRead,
  Shop,
} from "src/client";
import { YearWeek } from "src/modules/Globals";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import IsOnlineMixin from "src/modules/IsOnlineMixin";
import { WeekDays } from "src/modules/WeekUtils";
import { useBaseStore } from "src/stores/base";
import { defineComponent } from "vue";
import { getYearWeek } from "src/modules/WeekUtils";
import { productListItemFromRead, productListWeekFromRead } from "src/Convert";
import { useAuthStore } from "src/stores/auth";

type CustomIngredientCategory = IngredientCategory & {
  items?: ProductListItemRead[];
  custom?: boolean; // Custom frontend-only category flag
};

interface CategoriesMapping {
  [id: number]: CustomIngredientCategory;
}

interface QueryInterface {
  task?: number | null;
  year?: number;
  week?: number;
  shop?: number;
}

export default defineComponent({
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    weekSelect,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ProductListItemView,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ProductListItems,
  },
  mixins: [HandleErrorsMixin, IsOnlineMixin],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();

    let showCompleted = this.$q.localStorage.getItem("productsShowCompleted");
    if (showCompleted === null) {
      showCompleted = true;
    }

    return {
      store,
      storeAuth,
      // $query: useQuery(),
      loading: false,
      updating: false,
      saving: false,
      showCompleted: Boolean(showCompleted),
      createItem: "",
      markAlreadyCompleted: false,
      // week: {
      //   year: null,
      //   week: null,
      // },
      viewItem: undefined as ProductListItemRead | undefined,
      canSyncFlag: false,
      WeekDays,
    };
  },
  mounted() {
    void this.$nextTick(() => {
      this.onLoad();
    });
  },
  methods: {
    onLoad() {
      this.canSyncFlag = Boolean(
        this.$q.localStorage.has("local_productlist_updated")
      );
      if (this.isOnLine) {
        if (this.canSync) {
          this.$q.notify({
            type: "info",
            caption:
              "Рекомендуется выполнить синхронизацию изменений с сервером",
          });
        }
        this.loadShops();
        this.loadIngredientCategories();
        // if (this.$q.localStorage.has('local_productlist_updated')) {
        //   this.syncLocal();
        // }

        // this.loadList();
      } else {
        let local_cache = this.$q.localStorage.getItem("local_productlist") as
          | ProductListWeekRead
          | undefined;
        if (local_cache) {
          this.store.product_list = local_cache;
        }

        let shopsCache = this.$q.localStorage.getItem("shops") as
          | Shop[]
          | undefined;
        if (shopsCache) {
          this.store.shops = shopsCache;
        }

        let ingCategoryCache = this.$q.localStorage.getItem(
          "ing_categories"
        ) as IngredientCategory[];
        if (ingCategoryCache) {
          this.store.ingredient_categories = ingCategoryCache;
        }
      }
    },
    onWeekUpd() {
      this.loadList();
      this.loadWeekPlan();
    },
    loadList() {
      if (!this.week?.year || !this.week?.week) {
        return;
      }
      let payload = {
        year: this.week?.year,
        week: this.week?.week,
      };
      this.loading = true;

      this.store
        .loadProductListWeek(payload)
        .then(() => {
          this.loading = false;
          let argTask = (this.$query as QueryInterface).task;
          if (!this.viewItem && argTask) {
            this.selectItemByID(argTask);
          }

          let rewriteLocal = !this.$q.localStorage.has(
            "local_productlist_updated"
          );
          if (rewriteLocal) {
            this.syncServer();
          }
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка загрузки списка продуктов");
        });
    },
    loadShops() {
      this.store
        .loadShops({ pageSize: 1000 })
        .then((resp) => {
          this.$q.localStorage.set("shops", resp);
        })
        .catch((err: CustomAxiosError) => {
          this.handleErrors(err, "Ошибка загрузки списка магазинов");
          this.store.shops = this.$q.localStorage.getItem("shops");
        });
    },
    loadIngredientCategories() {
      this.store
        .loadIngredientCategories({ pageSize: 1000 })
        .then((resp) => {
          this.$q.localStorage.set("ing_categories", resp);
        })
        .catch((err: CustomAxiosError) => {
          this.handleErrors(
            err,
            "Ошибка загрузки списка категорий ингредиентоа"
          );
          this.store.shops = this.$q.localStorage.getItem("ing_categories");
        });
    },
    syncServer() {
      console.debug("SyncServer");
      this.$q.localStorage.set("local_productlist", this.store?.product_list);

      if (!this.isOnLine) {
        this.$q.localStorage.set("local_productlist_updated", true);
      }
    },
    askSyncLocal() {
      this.$q
        .dialog({
          title: "Подтверждение",
          message: `Вы уверены что хотите выполнить синхронизацию? Данные на сервере будут заменены локальным списком продуктов`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.syncLocal();
        });
    },
    askDiscardSync() {
      this.$q
        .dialog({
          title: "Подтверждение",
          message: `Вы уверены что хотите удалить локальные данные синхронизации? Это действие необратимо, локальный список продуктов будет стерт.`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.discardSync();
        });
    },
    discardSync() {
      this.$q.localStorage.remove("local_productlist_updated");
      this.$q.localStorage.remove("local_productlist");
      this.$q.notify({
        type: "warning",
        caption: "Данные синхронизации удалены",
        icon: "delete",
      });
      this.canSync = false;
      this.syncServer();
    },
    syncLocal() {
      this.$q.notify({
        type: "info",
        caption: "Синхронизация изменений с сервером...",
        icon: "cloud_sync",
      });

      this.loading = true;

      let payload = productListWeekFromRead(
        this.$q.localStorage.getItem("local_productlist")
      );
      console.debug("SyncLocal: ", payload);

      this.store
        .saveProductListWeek(payload)
        .then(() => {
          this.loading = false;
          this.$q.notify({
            type: "positive",
            caption: "Список продуктов успешно синхронизирован",
          });
          this.$q.localStorage.remove("local_productlist_updated");
          this.canSync = false;

          // this.loadList();
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка синхронизации списка продуктов");
        });
    },
    updateItem(item: ProductListItemRead, reload: boolean) {
      if (!item) {
        return;
      }
      if (this.markAlreadyCompleted) {
        if (item.is_completed) {
          item.already_completed = item.is_completed;
        }
      } else if (item.already_completed) {
        item.is_completed = true;
      }
      if (!this.isOnLine) {
        console.debug("Upd item: ", item);
        // Update offline data
        if (this.store.product_list) {
          this.store.product_list.items =
            this.store.product_list?.items?.map((i) => {
              if (i.id == item.id) {
                // console.debug(resp);
                return item;
              }
              return i;
            }) || [];
        }
        this.syncServer();
        return;
      }
      let payload = productListItemFromRead(Object.assign({}, item));
      this.saving = true;

      this.store
        .updateProductListItem(payload)
        .then((resp) => {
          if (this.store.product_list) {
            this.store.product_list.items =
              this.store.product_list?.items?.map((i) => {
                if (i.id == item.id) {
                  // console.debug(resp);
                  return resp;
                }
                return i;
              }) || [];
          }
          if (reload) {
            this.loadList();
          }
          this.saving = false;
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false;
          this.handleErrors(err, "Ошибка сохранения списка продуктов");
        });
    },
    // deleteItem(item) {},
    regenerateList() {
      if (!this.week.year || !this.week.week) {
        return;
      }
      let payload = {
        year: this.week.year,
        week: this.week.week,
      };
      this.loading = true;

      this.store
        .generateProductListWeek(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка обновления списка продуктов");
        });
    },
    openItem(item: ProductListItemRead) {
      console.debug("Open item: ", item);
      this.viewItem = item;
      // this.$query.task = item.id;
    },
    createNewItem() {
      let payload = {
        title: this.createItem,
        week: this.store.product_list?.id,
        amount: 1,
        amount_type: "items",
      };
      this.createItem = "";

      this.saving = true;
      this.store
        // @ts-expect-error: ProductListItem will be created
        .createProductListItem(payload)
        .then((resp) => {
          this.saving = false;
          this.viewItem = resp;
          if (this.store.product_list) {
            this.store.product_list.items.push(resp);
          }
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false;
          this.handleErrors(err, "Ошибка создания задачи");
        });
    },
    selectItemByID(val: number) {
      let res = this.store.product_list?.items.filter((i) => i.id == val);
      if (res && res.length > 0) {
        this.viewItem = res[0];
      }
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
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка загрузки плана");
        });
    },
    categoryHasShop(cat: IngredientCategory) {
      // if (cat.custom) {
      //   return true;
      // }
      if (!cat.sorting) {
        return;
      }
      return cat.sorting.find((s) => s.shop.id == this.sortShop);
    },
    sendList() {
      let payload = {
        year: this.week?.year,
        week: this.week?.week,
      };
      this.$q.loading.show({
        group: "sending",
        message: "Отправка списка...",
        delay: 400, // ms
      });

      this.store
        .productListSend(payload)
        .then(() => {
          this.$q.loading.hide("sending");
          this.$q.notify({
            type: "positive",
            message: `Список успешно отправлен`,
          });
        })
        .catch((err: CustomAxiosError) => {
          this.$q.loading.hide("sending");
          this.handleErrors(err, "Ошибка отправки списка");
        });
    },
  },
  computed: {
    week: {
      get(): YearWeek {
        let [year, week] = getYearWeek();
        return {
          year: (this.$query as QueryInterface).year || year,
          week: (this.$query as QueryInterface).week || week,
        };
      },
      set(val: YearWeek) {
        (this.$query as QueryInterface).year = val.year || undefined;
        (this.$query as QueryInterface).week = val.week || undefined;
      },
    },
    sortShop: {
      get() {
        return (this.$query as QueryInterface).shop || null;
      },
      set(val: number | null) {
        (this.$query as QueryInterface).shop = val || undefined;
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
            if (!a.day || !b.day) {
              return 0;
            }
            return a.day - b.day;
          });
        }
        return res;
      },
      set(newValue: ProductListItemRead[]) {
        // console.debug('set: ', newValue, this.store.product_list.items);
        if (this.store.product_list?.items == newValue) {
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
        let categoriesArr: CustomIngredientCategory[] =
          this.ingredientCategories.slice();

        categoriesArr.forEach((item, idx) => (categoriesArr[idx].items = [])); // Add items array

        let categories: CategoriesMapping = categoriesArr.reduce(
          (obj: CategoriesMapping, cur: CustomIngredientCategory) =>
            ({
              ...obj,
              [cur.id]: cur,
            } as CategoriesMapping),
          {} as CategoriesMapping
        ); // Convert to object
        let items = this.listItems.slice();
        let itemsCompleted = items.filter((i) => i?.is_completed);
        items = items.filter((i) => itemsCompleted.indexOf(i) === -1);

        for (let [idx, item] of items.entries()) {
          let catItem = item?.ingredient?.category;
          if (!catItem) continue;
          let cat = categories[catItem?.id];
          if (!cat || !cat.items) continue;
          cat.items.push(Object.assign({}, item));
          delete items[idx];
        }

        // @ts-expect-error Custom category
        categories[-1] = {
          id: -1,
          title: "Остальные",
          items: items.filter((i) => i).slice(),
          custom: true,
        };
        // @ts-expect-error Custom category
        categories[-2] = {
          id: -1,
          title: "Завершенные",
          items: itemsCompleted,
          custom: true,
        };
        let categoriesList: CustomIngredientCategory[] = [
          ...(Object.values(categories) as CustomIngredientCategory[]),
        ];

        categoriesList.sort((a, b) => {
          if (a.custom) {
            return 1;
          } else if (b.custom) {
            return -1;
          }

          let aSort = a.sorting.find((s) => s?.shop?.id == this.sortShop);
          let bSort = b.sorting.find((s) => s?.shop?.id == this.sortShop);
          if (!aSort?.num || !bSort?.num) {
            return 0;
          }

          return aSort?.num - bSort?.num;
        });

        return categoriesList;
      },
      set(newValue: ProductListItemRead[]) {
        if (
          !this.store.product_list ||
          this.store.product_list.items == newValue
        ) {
          return;
        }
        this.store.product_list.items = newValue;
      },
    },
    shops() {
      return this.store.shops;
    },
    ingredientCategories() {
      return this.store.ingredient_categories;
    },
    completedPrc() {
      let itemsCompleted = this.store.product_list?.items.filter(
        (i) => i.is_completed
      )?.length;
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
      set(val: boolean) {
        this.canSyncFlag = val;
      },
    },
    pricesCompleted() {
      return this.listItemsRaw
        .filter((i) => i.is_completed && !i.already_completed)
        .map((i) => i.price_full)
        .reduce((a, b) => a + b, 0);
    },
    pricesTotal() {
      return this.listItemsRaw
        .filter((i) => !i.already_completed)
        .map((i) => i.price_full)
        .reduce((a, b) => a + b, 0);
    },
    productsWithoutPrice() {
      return this.listItemsRaw.filter((i) => !i.price_full).length;
    },
    canEdit() {
      return this.storeAuth.hasPerm("recipes.change_productlistitem");
    },
    // viewItem: {
    //   get() {
    //     return (this.$query as QueryInterface).task;
    //   },
    //   set(val: string | null) {
    //     (this.$query as QueryInterface).task = val;
    //   },
    // },
  },
  watch: {
    showCompleted(val) {
      this.$q.localStorage.set("productsShowCompleted", val);
    },
  },
});
</script>
