<template>
  <q-page padding>
    <q-table
      title="Ингредиенты"
      :rows="ingredients?.results"
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

<script>
import { useBaseStore } from 'src/stores/base';
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
    name: 'min_pack_size',
    label: 'Размер упаковки',
    field: (row) => (row.min_pack_size ? row.min_pack_size : '-'),
    required: true,
    sortable: true,
  },
  {
    name: 'price',
    label: 'Цена',
    field: (row) => (row.price ? row.price + ' ₺' : '-'),
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
    field: (row) => (row.need_buy ? 'Да' : 'Нет'),
    align: 'center',
    required: true,
    sortable: true,
    style: 'width: 50px;',
  },
  {
    name: 'edible',
    label: 'Съедобен',
    field: (row) => (row.edible ? 'Да' : 'Нет'),
    align: 'center',
    required: true,
    sortable: true,
    style: 'width: 50px;',
  },
];

export default {
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
      },
    };
  },
  mounted() {
    this.loadIngredients();
  },
  methods: {
    loadIngredients(props) {
      let payload = {};
      this.loading = true;

      let pagination = Object.assign({}, this.tablePagination);
      if (props) {
        pagination = props.pagination;
      } else {
        props = {};
      }

      Object.assign(payload, {
        search: props.filter || this.tableFilter,
        ordering: (pagination.descending ? '-' : '') + pagination.sortBy,
        page_size: pagination.rowsPerPage,
        page: pagination.page,
      });

      this.store
        .loadIngredients(payload)
        .then((resp) => {
          this.loading = false;
          this.tablePagination = Object.assign({}, props?.pagination, {
            rowsNumber: resp.data.count,
          });
        })
        .catch((err) => {
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    onRowClick(e, row, index) {
      this.$router.push({ name: 'ingredient', params: { id: row.id } }).catch((e) => {});
    },
  },
  computed: {
    ingredients() {
      return this.store.ingredients;
    },
  },
};
</script>
