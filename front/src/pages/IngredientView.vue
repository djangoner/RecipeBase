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
    <q-form class="q-my-md" @submit.prevent="saveIngredient()" v-if="ingredient">
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
          <q-select
            v-model.number="ingredient.category"
            :options="ingredientCategories || []"
            label="Категория"
            option-label="title"
            option-value="id"
            map-options
            emit-value
            options-dense
            clearable
            filled
          >
          </q-select>
          <q-input
            v-model.number="ingredient.min_pack_size"
            label="Размер упаковки"
            filled
          ></q-input>
          <q-input
            v-model.number="ingredient.item_weight"
            label="Вес одной штуки"
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

          <q-img
            v-if="ingredient.image"
            :src="ingredient.image"
            height="100px"
            fit="contain"
          ></q-img>

          <q-toggle v-model="ingredient.need_buy" label="Требует покупки"> </q-toggle>
          <q-toggle v-model="ingredient.edible" label="Съедобный"> </q-toggle>
        </q-card-section>
        <q-card-actions class="q-col-gutter-x-md q-mx-none q-pb-md">
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

<script lang="ts">
import { ingredientFromRead } from 'src/Convert';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { useBaseStore } from 'src/stores/base';
import { defineComponent } from 'vue';

const defaultIngredient = {
  title: '',
  description: '',
  need_buy: true,
  edible: true,
};

export default defineComponent({
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      saving: false,
      deleting: false,
      requiredRule: (val: string | number | undefined) => !!val || 'Обязательное поле',
    };
  },
  mounted() {
    this.loadIngredient();
    if (!this.ingredientCategories) {
      this.loadIngredientCategories();
    }
  },
  beforeRouteUpdate(to) {
    this.loadIngredient(parseInt(to.params.id as string));
  },
  methods: {
    loadIngredient(load_id?: string | number | undefined) {
      let id: string | number = load_id || (this.$route.params.id as string);

      if (id == 'new') {
        this.resetData();
        return;
      }

      if (typeof id == 'string') {
        id = parseInt(id);
      }

      this.loading = true;
      this.store
        .loadIngredient(id)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиента');
        });
    },
    loadIngredientCategories() {
      let payload = {
        page_size: 1000,
      };
      // this.loading = true;

      this.store
        .loadIngredientCategories(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки категорий ингредиентов');
        });
    },
    resetData() {
      // @ts-expect-error: Ingredient will be created
      this.store.ingredient = Object.assign({}, defaultIngredient);
    },
    saveIngredient() {
      let payload = ingredientFromRead(this.ingredient);
      this.saving = true;

      let isCreating = !this.exists;
      let method = isCreating ? this.store.createIngredient : this.store.saveIngredient;

      // payload.category =
      //   typeof payload.category == 'number' ? payload.category : payload.category?.id;
      // if (!typeof payload.category == 'number') {
      //   payload.category = payload.category;
      // }

      method(payload)
        .then((resp) => {
          this.saving = false;

          if (isCreating) {
            void this.$router.replace({ name: 'ingredient', params: { id: resp.id } });
          }

          let created_tx = isCreating ? 'создан' : 'сохранен';
          this.$q.notify({
            type: 'positive',
            message: `Ингредиент успешно ${created_tx}`,
          });
        })
        .catch((err: CustomAxiosError) => {
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
          void this.deleteIngredient().then(() => {
            this.$q.notify({
              type: 'positive',
              message: `Ингредиент успешно удален`,
              icon: 'delete',
            });
            void this.$router.replace({ name: 'ingredients' });
          });
        });
    },
    deleteIngredient(): Promise<void> {
      return new Promise((resolve, reject) => {
        if (!this.exists || !this.ingredient) {
          reject();
          return;
        }
        this.deleting = true;
        this.store
          .deleteIngredient(this.ingredient.id)
          .then(() => {
            resolve();
            this.deleting = false;
          })
          .catch((err: CustomAxiosError) => {
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
    ingredientCategories() {
      return this.store.ingredient_categories;
    },
    exists() {
      return Boolean(this.ingredient?.id);
    },
  },
});
</script>
