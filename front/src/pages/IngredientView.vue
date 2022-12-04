<template>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-pb-md">
      <div>
        <q-btn icon="arrow_back" size="sm" @click="$router.go(-1)">Назад</q-btn>
      </div>
      <div>
        <q-btn
          v-if="exists"
          icon="add"
          size="sm"
          color="positive"
          @click="$router.push({ name: 'ingredient', params: { id: 'new' } })"
          >Новый ингредиент</q-btn
        >
      </div>
    </div>
    <q-form class="q-mt-md" @submit.prevent="saveIngredient()" v-if="ingredient">
      <q-card padding>
        <q-card-section class="q-col-gutter-y-md">
          <!-- Main fields -->
          <q-input
            v-model="ingredient.title"
            label="Название ингредиента"
            :rules="[requiredRule]"
            hide-bottom-space
            filled
          ></q-input>
          <q-input
            v-model.number="ingredient.min_pack_size"
            label="Размер упаковки"
            filled
          ></q-input>

          <q-input v-model.number="ingredient.price" label="Цена (₺)" filled></q-input>

          <q-input
            v-model="ingredient.description"
            type="textarea"
            label="Описание"
            filled
            autogrow
          >
          </q-input>
          <q-toggle v-model="ingredient.need_buy" label="Требует покупки"> </q-toggle>
          <q-toggle v-model="ingredient.edible" label="Съедобный"> </q-toggle>
        </q-card-section>
        <q-card-actions class="q-col-gutter-x-md q-mx-none">
          <div>
            <q-btn
              type="submit"
              icon="save"
              color="positive"
              :loading="saving"
              :disable="deleting"
              >Сохранить</q-btn
            >
          </div>
          <div>
            <q-btn
              v-if="exists"
              @click="askDelete()"
              icon="delete"
              color="negative"
              :loading="deleting"
              :disable="saving"
              >Удалить</q-btn
            >
          </div>
        </q-card-actions>
      </q-card>
    </q-form>

    <q-inner-loading :showing="loading" />
  </q-page>
</template>

<script>
import { useBaseStore } from 'src/stores/base';

const defaultIngredient = {
  title: '',
  description: '',
  need_buy: true,
  edible: true,
};

export default {
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      saving: false,
      deleting: false,
      requiredRule: (val) => !!val || 'Обязательное поле',
    };
  },
  mounted() {
    this.loadIngredient();
  },
  beforeRouteUpdate(to) {
    this.loadIngredient(to.params.id);
  },
  methods: {
    loadIngredient(load_id) {
      let id = load_id || this.$route.params.id;

      if (id == 'new') {
        this.resetData();
        return;
      }

      let payload = {
        id: id,
      };
      this.loading = true;

      this.store
        .loadIngredient(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиента');
        });
    },
    resetData() {
      this.store.ingredient = Object.assign({}, defaultIngredient);
    },
    saveIngredient() {
      let payload = Object.assign({}, this.ingredient);
      this.saving = true;

      let isCreating = !this.exists;
      let method = isCreating ? this.store.createIngredient : this.store.saveIngredient;

      method(payload)
        .then((resp) => {
          this.saving = false;

          if (isCreating) {
            this.$router.replace({ name: 'ingredient', params: { id: resp.data.id } });
          }

          let created_tx = isCreating ? 'создан' : 'сохранен';
          this.$q.notify({
            type: 'positive',
            message: `Ингредиент успешно ${created_tx}`,
          });
        })
        .catch((err) => {
          this.saving = false;
          this.handleErrors(err, 'Ошибка сохранения ингредиента');
        });
    },
    askDelete() {
      this.$q
        .dialog({
          title: 'Подтверждение',
          message:
            'Вы уверены что хотите удалить этот ингредиент? Он будет удален из всех используемых рецептов и из списка продуктов.',
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.deleteIngredient().then(() => {
            this.$q.notify({
              type: 'positive',
              message: `Ингредиент успешно удален`,
              icon: 'delete',
            });
            this.$router.replace({ name: 'ingredients' });
          });
        });
    },
    deleteIngredient() {
      return new Promise((resolve, reject) => {
        if (!this.exists) {
          reject();
          return;
        }
        this.deleting = true;
        this.store
          .deleteIngredient(this.ingredient)
          .then(() => {
            resolve();
            this.deleting = false;
          })
          .catch((err) => {
            reject();
            this.deleting = false;
            this.handleErrors(err, 'Ошибка удаления ингредиента');
          });
      });
    },
  },
  computed: {
    ingredient() {
      return this.store.ingredient;
    },
    exists() {
      return Boolean(this.ingredient?.id);
    },
  },
};
</script>
