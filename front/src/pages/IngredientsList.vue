<template>
  <q-page padding>
    <q-table
      title="Ингредиенты"
      :rows="ingredients || []"
      :columns="tableColumns"
      :loading="loading"
      :filter="tableFilter"
      :rows-per-page-options="[1, 5, 10, 15, 20, 50, 100]"
      @row-click="onRowClick"
      v-model:pagination="tablePagination"
      @request="loadIngredients"
      binary-state-sort
      :dense="$q.screen.lt.md"
    >
      <!-- Search & create new -->
      <template v-slot:top-right>
        <q-btn
          @click="$router.push({ name: 'ingredient', params: { id: 'new' } })"
          class="q-mr-md"
          icon="add"
          size="sm"
          color="positive"
          >Новый ингредиент</q-btn
        >
        <q-input
          borderless
          dense
          debounce="300"
          v-model="tableFilter"
          placeholder="Поиск"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>

      <!-- Need buy -->
      <template #body-cell-need_buy="props">
        <q-td class="text-center" :props="props">
          <q-badge v-if="props.row.need_buy" color="green">Да</q-badge>
          <q-badge v-else color="orange">Нет</q-badge>
        </q-td>
      </template>

      <!-- Edible -->
      <template #body-cell-edible="props">
        <q-td class="text-center" :props="props">
          <q-badge v-if="props.row.edible" color="green">Да</q-badge>
          <q-badge v-else color="orange">Нет</q-badge>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script lang="ts">
import { useBaseStore } from 'src/stores/base';
import { IngredientRead } from 'src/client';
import { defineComponent } from 'vue';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { TablePagination, TablePropsOnRequest } from 'src/modules/Globals';
import { QTableProps } from 'quasar';
let tableColumns = [
  {
    name: 'title',
    label: 'Название',
    align: 'left',
    field: 'title',
    required: true,
    sortable: true,
  },
  {
    name: 'category',
    label: 'Категория',
    align: 'left',
    field: (row: IngredientRead) => row?.category?.title || '-',
    required: true,
    sortable: true,
  },
  {
    name: 'min_pack_size',
    label: 'Размер упаковки',
    field: (row: IngredientRead) => (row.min_pack_size ? row.min_pack_size : '-'),
    required: true,
    sortable: true,
  },
  {
    name: 'price',
    label: 'Цена',
    field: (row: IngredientRead) => (row.price ? String(row.price) + ' ₺' : '-'),
    required: true,
    sortable: true,
  },
  {
    name: 'used_times',
    label: 'В рецептах',
    field: 'used_times',
    required: true,
    sortable: true,
    style: 'width: 50px;',
  },
  {
    name: 'need_buy',
    label: 'Требует покупки',
    field: (row: IngredientRead) => (row.need_buy ? 'Да' : 'Нет'),
    align: 'center',
    required: true,
    sortable: true,
    style: 'width: 50px;',
  },
  {
    name: 'edible',
    label: 'Съедобен',
    field: (row: IngredientRead) => (row.edible ? 'Да' : 'Нет'),
    align: 'center',
    required: true,
    sortable: true,
    style: 'width: 50px;',
  },
] as QTableProps['columns'];

export default defineComponent({
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      tableFilter: '',
      tableColumns,
      tablePagination: {
        rowsPerPage: 20,
        page: 1,
        sortBy: 'title',
        descending: false,
      } as TablePagination,
    };
  },
  mounted() {
    this.loadIngredients();
  },
  methods: {
    loadIngredients(props?: TablePropsOnRequest) {
      let payload = {};
      this.loading = true;

      let pagination: TablePagination = Object.assign({}, this.tablePagination);
      if (props && props.pagination) {
        pagination = props.pagination;
      }

      Object.assign(payload, {
        search: this.tableFilter,
        ordering: (pagination.descending ? '-' : '') + String(pagination.sortBy),
        page_size: pagination.rowsPerPage,
        page: pagination.page,
      });

      this.store
        .loadIngredients(payload, true)
        .then((resp) => {
          this.loading = false;
          this.tablePagination = Object.assign({}, props?.pagination, {
            rowsNumber: resp.count,
          });
        })
        .catch((err: CustomAxiosError) => {
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    onRowClick(e: Event, row: IngredientRead) {
      void this.$router.push({ name: 'ingredient', params: { id: row.id } });
    },
  },
  computed: {
    ingredients() {
      return this.store.ingredients;
    },
  },
});
</script>
