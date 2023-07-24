<template>
  <q-page>
    <!-- Top bar -->
    <week-select
      v-model="week"
      @update:model-value="onWeekUpd()"
    />
    <q-linear-progress
      :value="completedPrc"
      :indeterminate="saving"
      :instant-feedback="saving"
      :animation-speed="500"
    />
    <!-- Top warnings -->
    <status-websocket />
    <already-completed-banner :show="markAlreadyCompleted" />
    <not-actual-list-banner
      :show="productList && !isActual"
      @reload="$refs.menu.regenerateList()"
    />
    <!-- Modals -->
    <product-list-item-view
      v-model="viewItem"
      :week="week"
      :can-edit="canEdit"
      @update-item="updateItem"
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
        />
      </div>
      <div>
        <!-- <q-toggle
          v-model="showCompleted"
          label="Показать завершенные"
          dense
        /> -->
        <q-toggle
          v-model="markAlreadyCompleted"
          label="Отметить есть"
          dense
        />
      </div>

      <q-space />
      <div>
        <product-list-search @select="viewItem = $event" />
      </div>
      <div>
        <product-list-menu
          ref="menu"
          v-model:mark-already-completed="markAlreadyCompleted"
          v-model:show-already-completed="showAlreadyCompleted"
          v-model:show-completed="showCompleted"
          :week="week"
          :can-sync="canSync"
          @loading="loading = $event"
          @can-sync-flag="canSyncFlag = $event"
          @dialog-obj="dialog_obj = $event"
          @ask-sync="askSyncLocal()"
        />
      </div>
    </div>

    <!-- Product list -->
    <q-list class="row column q-col-gutter-y-md q-py-md q-px-none q-px-sm-lg">
      <!-- New item -->
      <add-product-item
        v-if="storeAuth.hasPerm('recipes.add_productlistitem')"
        @select="viewItem = $event"
        @create="createNewItem"
      />

      <!-- Prices total -->
      <div class="row q-gutter-x-sm q-px-md q-pt-xs">
        <q-badge color="grey">
          {{ pricesCompleted }}₺ / {{ pricesTotal }}₺

          <q-tooltip>~ уже потрачено / стоимость продуктов</q-tooltip>
        </q-badge>
        <q-badge color="grey">
          Вес: {{ weightCompleted }} / {{ weightTotal }} кг
        </q-badge>
        <q-badge
          v-if="productsWithoutPrice"
          color="grey"
        >
          {{ productsWithoutPrice }}/{{ listItemsRaw.length }} продуктов без цены
        </q-badge>
      </div>

      <!-- Product list item -->
      <template v-if="sortShop">
        <template v-for="cat of listItemsCategories">
          <div
            v-if="cat.items && cat.items.length > 0"
            :key="cat.id"
          >
            <div class="row q-mx-md">
              <h5
                class="q-my-sm"
                :class="categoryHasShop(cat) ? 'text-primary' : 'text-orange'"
              >
                {{ cat.title }}
                <q-tooltip v-if="cat.sorting">
                  <b>Магазины:</b>
                  <div
                    v-for="sort of cat.sorting"
                    :key="sort.id"
                  >
                    - {{ sort.shop.title }}
                  </div>
                  <div v-if="cat.sorting.length < 1">
                    Нет магазинов
                  </div>
                </q-tooltip>
              </h5>
            </div>

            <product-list-items
              :key="cat.id"
              :list-items="cat.items"
              :week="week"
              :can-edit="canEdit"
              @open-item="openItem"
              @update-item="updateItem"
            />
          </div>
        </template>
      </template>
      <template v-else>
        <product-list-items
          :key="0"
          :list-items="listItems"
          :week="week"
          :can-edit="canEdit"
          @open-item="openItem"
          @update-item="updateItem"
        />
      </template>
    </q-list>

    <div
      v-if="!showCompleted"
      class="flex flex-center"
    >
      <q-btn
        flat
        label="Показать завершенные"
        icon="expand_more"
        no-caps
        size="sm"
        dense
        @click="showCompleted = true"
      />
    </div>
    <div
      v-else-if="showCompleted"
      class="flex flex-center"
    >
      <q-btn
        flat
        label="Скрыть завершенные"
        icon="expand_less"
        no-caps
        size="sm"
        dense
        @click="showCompleted = false"
      />
    </div>

    <q-inner-loading :showing="loading" />
  </q-page>
</template>

<script lang="ts">
import ProductListSearch from '../components/Products/ProductListSearch.vue'
import AddProductItem from '../components/Products/AddProductItem.vue'
import NotActualListBanner from "../components/Products/NotActualListBanner.vue"
import ProductListMenu from "../components/Products/ProductListMenu.vue"
import AlreadyCompletedBanner from "../components/Products/AlreadyCompletedBanner.vue"
import ProductListItems from "components/ProductListItems.vue"
import ProductListItemView from "components/ProductListItemView.vue"
import weekSelect from "components/WeekSelect.vue"
import { IngredientCategory, ProductListItemRead } from "src/client"
import { YearWeek } from "src/modules/Globals"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import IsOnlineMixin from "src/modules/IsOnlineMixin"
import { WeekDays } from "src/modules/WeekUtils"
import { useBaseStore } from "src/stores/base"
import { defineComponent } from "vue"
import { getYearWeek } from "src/modules/WeekUtils"
import { productListItemFromRead } from "src/Convert"
import { useAuthStore } from "src/stores/auth"
import { useQuery } from "@oarepo/vue-query-synchronizer"
import {
  productListGetChanged,
  productListGetOffline,
  productListMarkUnchanged,
  ProductListItemSyncable,
  productListUpdateFromServer,
  productListUpdateItem,
  productListUpdateRawItem,
} from "src/modules/ProductListSync"
import WorkerMessagesMixin, { WorkerMessage } from "src/modules/WorkerMessages"
import { DialogChainObject } from "quasar"
import StatusWebsocket from "src/components/Status/StatusWebsocket.vue"
import { sortChains } from "src/modules/Utils"

type CustomIngredientCategory = IngredientCategory & {
  items?: ProductListItemRead[]
  custom?: boolean // Custom frontend-only category flag
}

interface CategoriesMapping {
  [id: number]: CustomIngredientCategory
}

interface QueryInterface {
  task?: number | null
  year?: number
  week?: number
  shop?: number
}

export default defineComponent({
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    weekSelect,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ProductListItemView,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ProductListItems,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    AlreadyCompletedBanner,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    StatusWebsocket,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ProductListMenu,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    NotActualListBanner, AddProductItem, ProductListSearch
  },
  mixins: [HandleErrorsMixin, IsOnlineMixin, WorkerMessagesMixin],
  data() {
    const store = useBaseStore()
    const storeAuth = useAuthStore()

    const showCompleted = this.$q.localStorage.getItem("productsShowCompleted") ?? true
    const showAlreadyCompleted = this.$q.localStorage.getItem("productsShowAlreadyCompleted") ?? true

    return {
      store,
      storeAuth,
      $query: useQuery(),
      loading: false,
      updating: false,
      saving: false,
      showCompleted: Boolean(showCompleted),
      showAlreadyCompleted: Boolean(showAlreadyCompleted),
      markAlreadyCompleted: false,
      listRawLast: null as ProductListItemRead[] | null,
      // week: {
      //   year: null,
      //   week: null,
      // },
      viewItem: undefined as ProductListItemRead | undefined,
      canSyncFlag: false,
      changedCount: null as number | null,
      dialog_obj: null as DialogChainObject | null,
      WeekDays,
    }
  },
  computed: {
    week: {
      get(): YearWeek {
        const [year, week] = getYearWeek()
        return {
          year: (this.$query as QueryInterface).year || year,
          week: (this.$query as QueryInterface).week || week,
        }
      },
      set(val: YearWeek) {
        ; (this.$query as QueryInterface).year = val.year || undefined
          ; (this.$query as QueryInterface).week = val.week || undefined
      },
    },
    sortShop: {
      get() {
        return (this.$query as QueryInterface).shop || null
      },
      set(val: number | null) {
        ; (this.$query as QueryInterface).shop = val || undefined
      },
    },
    listItemsRaw() {
      return this.store.product_list?.items || []
    },
    listItems: {
      get() {
        let res = this.store.product_list?.items || []
        res = res.slice()

        if (res) {
          // Sort by is_completed(false first), then day(lower first)
          if (!this.showCompleted) {
            res = res.filter((i) => !i.is_completed)
          }
          if (!this.showAlreadyCompleted) {
            res = res.filter((i) => !i.already_completed)
          }
          sortChains(res, [
            (a, b) => {
              // Is completed
              if (a.is_completed && !b.is_completed) {
                return 1
              } else if (b.is_completed && !a.is_completed) {
                return -1
              }
            },
            (a, b) => {
              // Priority
              if (a.priority && b.priority) {
              return a.priority - b.priority
              }
            },
            (a, b) => {
              // Name sort (If completed)
              if (a.is_completed && b.is_completed) {
                if (a.title < b.title) {
                  return -1
                }
                if (a.title > b.title) {
                  return 1
                }
              }
            },
            (a, b) => {
              // Buy later
              return new Date(a.buy_later || 0) - new Date(b.buy_later || 0)
            },
            (a, b) => {
              // Days sort
              if (!a.day || !b.day) {
                return 0
              }
              return a.day - b.day
            },
          ])
        }
        return res
      },
      set(newValue: ProductListItemRead[]) {
        // console.debug('set: ', newValue, this.store.product_list.items);
        if (this.store.product_list?.items == newValue) {
          return
        }
        // this.store.product_list.items = newValue;
      },
    },
    listItemsCategories: {
      get() {
        if (!this.ingredientCategories) {
          return []
        }
        const categoriesArr: CustomIngredientCategory[] = this.ingredientCategories.slice()
        const today = new Date()

        categoriesArr.forEach((item, idx) => (categoriesArr[idx].items = [])) // Add items array

        const categories: CategoriesMapping = categoriesArr.reduce(
          (obj: CategoriesMapping, cur: CustomIngredientCategory) =>
          ({
            ...obj,
            [cur.id]: cur,
          } as CategoriesMapping),
          {} as CategoriesMapping
        ) // Convert to object
        let items = this.listItems.slice()
        const itemsCompleted = items.filter((i) => i?.is_completed)
        const itemsLater = items.filter((i) => i.buy_later && new Date(i.buy_later) > today)
        // Remove items from other lists. These items will not be in categorized list.
        items = items.filter((i) => itemsCompleted.indexOf(i) === -1 && itemsLater.indexOf(i) === -1)
        console.debug("Sort: ", { itemsLater, itemsCompleted, items })

        for (const [idx, item] of items.entries()) {
          const catItem = item?.ingredient?.category
          if (!catItem) continue
          const cat = categories[catItem]
          if (!cat || !cat.items) continue
          cat.items.push(Object.assign({}, item))
          delete items[idx]
        }

        // @ts-expect-error Custom category
        categories[-1] = {
          id: -1,
          title: "Остальные",
          items: items.filter((i) => i).slice(),
          custom: true,
        }
        // @ts-expect-error Custom category
        categories[-2] = {
          id: -2,
          title: "Завершенные",
          items: itemsCompleted,
          custom: true,
        }
        // @ts-expect-error Custom category
        categories[-3] = {
          id: -3,
          title: "Отложенные",
          items: itemsLater,
          custom: true,
        }
        const categoriesList: CustomIngredientCategory[] = [...(Object.values(categories) as CustomIngredientCategory[])]

        categoriesList.sort((a, b) => {
          if (a.custom) {
            return 1
          } else if (b.custom) {
            return -1
          }

          const aSort = a.sorting.find((s) => s?.shop?.id == this.sortShop)
          const bSort = b.sorting.find((s) => s?.shop?.id == this.sortShop)
          if (!aSort?.num || !bSort?.num) {
            return 0
          }

          return aSort?.num - bSort?.num
        })

        return categoriesList
      },
      set(newValue: ProductListItemRead[]) {
        if (!this.store.product_list || this.store.product_list.items == newValue) {
          return
        }
        this.store.product_list.items = newValue
      },
    },
    shops() {
      return this.store.shops
    },
    ingredientCategories() {
      return this.store.ingredient_categories
    },
    completedPrc() {
      const items = this.store.product_list?.items?.filter((i) => !i.already_completed)

      const itemsCompleted = items?.filter((i) => i.is_completed)?.length
      const itemsTotal = items?.length

      if (!itemsCompleted || !itemsTotal) {
        return 0
      }
      return itemsCompleted / itemsTotal
    },
    completedCount() {
      return this.listItemsRaw.filter((i) => i.is_completed).length
    },
    productList() {
      return this.store.product_list
    },
    isActual() {
      return this.store.product_list?.is_actual
    },
    canSync: {
      get() {
        return this.isOnLine && this.canSyncFlag
      },
      set(val: boolean) {
        this.canSyncFlag = val
      },
    },
    pricesCompleted() {
      return this.listItemsRaw
        .filter((i) => i.is_completed && !i.already_completed)
        .map((i) => i.price_full)
        .reduce((a, b) => a + b, 0)
    },
    pricesTotal() {
      return this.listItemsRaw
        .filter((i) => !i.already_completed)
        .map((i) => i.price_full)
        .reduce((a, b) => a + b, 0)
    },
    weightCompleted() {
      const weight = this.listItemsRaw
        .filter((i) => i.is_completed && !i.already_completed)
        .filter((i) => i.amount_type == "g" && i.amount)
        .map((i) => i.amount)
        // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
        .reduce((a, b) => a + b, 0)
      if (!weight) {
        return 0
      }
      return (weight / 1000).toPrecision(1)
    },
    weightTotal() {
      const weight = this.listItemsRaw
        .filter((i) => !i.already_completed)
        .filter((i) => i.amount_type == "g" && i.amount)
        .map((i) => i.amount)
        // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
        .reduce((a, b) => a + b, 0)
      if (!weight) {
        return 0
      }
      return (weight / 1000).toPrecision(1)
    },
    productsWithoutPrice() {
      return this.listItemsRaw.filter((i) => !i.price_full).length
    },
    canEdit() {
      return this.storeAuth.hasPerm("recipes.change_productlistitem")
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
      this.$q.localStorage.set("productsShowCompleted", val)
    },
    showAlreadyCompleted(val) {
      this.$q.localStorage.set("productsShowAlreadyCompleted", val)
    },
    isOnLine(val, oldVal) {
      if (val && !oldVal && this.canSync) {
        void this.askSyncLocal()
      }
    },
    listItemsRaw: {
      deep: true,
      handler(val: ProductListItemRead[] | null) {
        const lastList = this.listRawLast
        // Update offline diff items
        if (val && lastList) {
          for (const item1 of val) {
            const item2 = lastList.find((x) => x.id === item1.id)
            const itemEq = item1 === item2

            if (!itemEq) {
              // itemsDiff.push(item1)
              void productListUpdateRawItem(item1)
              // console.debug("UPD DIFF: ", item1)
            }
          }
        }

        // Update current viewItem
        this.listRawLast = val ? val.slice() : []
        if (val && this.viewItem) {
          const currItem = this.listItemsRaw.find((i) => i.id == this.viewItem.id)
          if (currItem) {
            this.viewItem = currItem
            console.debug("Updated current viewItem")
          }
        }
      },
    },
  },
  created() {
    void this.$nextTick(() => {
      void this.onLoad()
    })
  },
  beforeUnmount() {
    if (this.dialog_obj) {
      try {
        this.dialog_obj.hide()
      } catch (error) {
        console.debug("Dialog hide error: ", error)
      }
    }
  },
  methods: {
    onWorkerMessage(msg: WorkerMessage) {
      const data = msg.data
      if (data.type == "product-list-sync-start") {
        this.$q.loading.show({
          group: "autosync",
          message: "Идет фоновая синхронизация...",
          delay: 100, // ms
        })
      } else if (data.type == "product-list-sync") {
        console.debug("Product list received worker signal, reloading...")
        if (this.dialog_obj) {
          this.dialog_obj.hide()
        }
        void this.$nextTick(() => {
          this.$q.loading.hide("autosync")
          this.canSyncFlag = false
          void this.onLoadCheckSync()
          if (this.canSyncFlag) {
            this.$q.notify({
              type: "warning",
              caption: "Похоже что последняя фоновая синхронизация завершилась с ошибкой",
            })
            this.askSyncLocal()
          } else {
            this.$q.notify({
              type: "positive",
              caption: "Фоновая синхронизация успешно завершена",
            })
          }
          this.loadList()
        })
      }
    },
    // eslint-disable-next-line @typescript-eslint/require-await
    async onLoad() {
      void this.onLoadCheckSync()
      void this.loadShops()
      void this.loadIngredientCategories()
      if (this.isOnLine) {
        if (this.canSync) {
          void this.askSyncLocal()
        }
      }
    },
    async onLoadCheckSync() {
      const changedItems = await productListGetChanged()
      this.canSyncFlag = Boolean(changedItems && changedItems.length > 0)
      if (changedItems) {
        this.changedCount = changedItems.length
      }
    },
    onWeekUpd() {
      this.loadList()
      this.loadWeekPlan()
    },
    async loadListOffline() {
      console.debug("Trying to load cached product list", this.week)
      if (this.week) {
        const changedItems = await productListGetChanged()
        this.canSyncFlag = Boolean(changedItems && changedItems.length > 0)
        if (changedItems) {
          this.changedCount = changedItems.length
        }
        //
        // this.changedCount = info.items.length
        await productListGetOffline(this.week.year, this.week.week).then((info) => {
          if (info) {
            this.store.product_list = Object.assign({}, info.week, { items: info.items })
          } else {
            this.$q.notify({
              type: "negative",
              caption: `Не найден сохраненный список покупок для ${this.week.year}.${this.week.week}`,
            })
          }
        })
      }
    },
    loadList() {
      if (!this.week?.year || !this.week?.week) {
        return
      }
      if (!this.isOnLine) {
        void this.loadListOffline()
        return
      }
      console.debug("Loading online list")
      const payload = {
        year: this.week?.year,
        week: this.week?.week,
      }
      this.loading = true

      this.store
        .loadProductListWeek(payload)
        .then(() => {
          this.loading = false
          const argTask = (this.$query as QueryInterface).task
          if (!this.viewItem && argTask) {
            this.selectItemByID(argTask)
          }
          this.syncSaveToLocal()
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки списка продуктов")
        })
    },
    loadShops() {
      this.store.loadShops({ pageSize: 1000 }).catch((err: CustomAxiosError) => {
        this.handleErrors(err, "Ошибка загрузки списка магазинов")
      })
    },
    loadIngredientCategories() {
      void this.store.loadIngredientCategories({ pageSize: 1000 })
    },
    syncSaveToLocal() {
      console.debug("syncSaveToLocal")

      if (this.isOnLine && this.store.product_list) {
        void productListUpdateFromServer(this.store.product_list)
        // this.$q.localStorage.set("local_productlist", this.store?.product_list);
      }

      if (!this.isOnLine) {
        this.$q.localStorage.set("local_productlist_updated", true)
      }
    },
    askSyncLocal() {
      this.dialog_obj = this.$q
        .dialog({
          title: `Синхронизация (элементов: ${this.changedCount || "-"})`,
          message: `Вы уверены что хотите выполнить синхронизацию?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          void this.syncLocal()
        })
    },
    async syncLocal() {
      if (!this.week) {
        return
      }
      console.debug("Running sync with server...")
      this.$q.notify({
        type: "info",
        caption: "Синхронизация изменений с сервером...",
        icon: "cloud_sync",
      })

      this.loading = true

      // const payload = productListWeekFromRead(
      //   this.$q.localStorage.getItem("local_productlist")
      // );
      // console.debug("SyncLocal: ", payload);
      const itemsChanged = await productListGetChanged()
      console.debug("Local items changed: ", itemsChanged)

      this.loading = false

      const getMsg = (idx: number) => {
        const prc = Math.round((idx / itemsChanged.length) * 100)
        return `Синхронизация...  ${prc}%`
      }
      const loading = this.$q.loading.show({
        group: "product-list-sync",
      })

      await this.store.syncProductListItems(
        itemsChanged,
        (idx: number) => {
          loading({ message: getMsg(idx) })
        },
        async (item: ProductListItemSyncable) => {
          await productListMarkUnchanged(item)
        }
      )
      this.$q.loading.hide("product-list-sync")
      this.$q.notify({
        type: "positive",
        caption: "Список покупок успешно синхронизирован",
      })
      void this.$nextTick(() => {
        this.canSyncFlag = false
        this.loadList()
      })
      // this.store
      //   .saveProductListWeek(payload)
      //   .then(() => {
      //     this.loading = false;
      //     this.$q.localStorage.remove("local_productlist_updated");
      //     this.canSync = false;

      //     // this.loadList();
      //   })
      //   .catch((err: CustomAxiosError) => {
      //     this.loading = false;
      //     this.handleErrors(err, "Ошибка синхронизации списка продуктов");
      //   });
    },
    async updateOfflineItem(item: ProductListItemRead) {
      console.debug("Upd item: ", item)
      // Update offline data
      let newKey: number | null = null
      if (this.store.product_list) {
        newKey = await productListUpdateItem(item) // Update in indexed DB
        this.canSyncFlag = true

        // @ts-expect-error custom model
        const itemId = this.store.product_list.items.findIndex((i) => i.idLocal === newKey)
        if (itemId !== undefined) {
          console.debug("Updated stored item: ", itemId)
          this.store.product_list.items[itemId] = item
        }
      }

      try {
        const registration = await navigator.serviceWorker.ready
        const tags = await registration.sync.getTags()
        const token = localStorage.getItem("authToken") || ""
        const syncTag = "product-list-sync:" + token

        if (!tags.find((t) => t.startsWith("product-list-sync"))) {
          await registration.sync.register(syncTag)
          console.debug("Background sync task created")
        } else {
          console.debug("Background sync task already waiting", tags)
        }
      } catch (error) {
        console.debug("Background sync request failed: ", error)
      }
      return newKey
    },
    updateItem(item: ProductListItemRead, reload: boolean) {
      if (!item) {
        return
      }
      if (this.markAlreadyCompleted) {
        if (item.is_completed) {
          item.already_completed = item.is_completed
        }
      } else if (item.already_completed) {
        item.is_completed = true
      }
      if (!this.isOnLine) {
        void this.updateOfflineItem(item)
        return
      }
      const payload = productListItemFromRead(Object.assign({}, item))
      this.saving = true

      this.store
        .updateProductListItem(payload)
        .then((resp) => {
          if (this.store.product_list) {
            this.store.product_list.items =
              this.store.product_list?.items?.map((i) => {
                if (i.id == item.id) {
                  // console.debug(resp);
                  return resp
                }
                return i
              }) || []
            void productListUpdateRawItem(item)
          }
          if (reload) {
            this.loadList()
          }
          this.saving = false
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false
          this.handleErrors(err, "Ошибка сохранения списка продуктов")
        })
    },
    // deleteItem(item) {},
    openItem(item: ProductListItemRead) {
      console.debug("Open item: ", item)
      this.viewItem = item
      // this.$query.task = item.id;
    },
    async createNewItem(title: string, override?: object) {
      if (!title) {
        return
      }
      const payload = {
        title: title,
        week: this.store.product_list?.id,
        amount: 1,
        amount_type: "items",
        priority: 3,
        is_completed: false,
        already_completed: false,
      } as ProductListItemRead

      if (override){
        Object.assign(payload, override)
      }

      if (!this.isOnLine) {
        const newKey = await this.updateOfflineItem(payload)
        console.debug("Offline item new key: ", newKey)
        await this.loadListOffline()
        console.debug("Fixing offline item view: ", newKey)

        // @ts-expect-error idLocal
        const item = this.store.product_list.items.find((i) => i.idLocal == newKey)
        console.debug("Created item: ", item, this.store.product_list?.items)
        if (item) {
          this.viewItem = item
        }
        return
      }

      this.saving = true
      this.store
        // @ts-expect-error: ProductListItem will be created
        .createProductListItem(payload)
        .then((resp) => {
          this.saving = false
          this.viewItem = resp
          if (this.store.product_list) {
            this.store.product_list.items.push(resp)
          }
          void productListUpdateRawItem(resp)
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false
          this.handleErrors(err, "Ошибка создания задачи")
        })
    },
    selectItemByID(val: number) {
      const res = this.store.product_list?.items.filter((i) => i.id == val)
      if (res && res.length > 0) {
        this.viewItem = res[0]
      }
    },
    loadWeekPlan() {
      if (!this.week?.year || !this.week?.week) {
        return
      }
      // if (!this.isOnLine){
      //   return
      // }
      const payload = {
        year: this.week.year,
        week: this.week.week,
      }
      this.loading = true

      this.store
        .loadWeekPlan(payload)
        .then(() => {
          this.loading = false
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false
          this.handleErrors(err, "Ошибка загрузки плана на неделю")
        })
    },
    categoryHasShop(cat: IngredientCategory) {
      // if (cat.custom) {
      //   return true;
      // }
      if (!cat.sorting) {
        return
      }
      return cat.sorting.find((s) => s.shop.id == this.sortShop)
    },
  },
})
</script>
