<template>
  <q-dialog
    v-model="imageFullscreen"
    full-height
    full-width
    v-if="previewImage"
  >
    <q-card
      class="column full-height q-pa-none"
      style="background: transparent"
      flat
    >
      <div class="absolute-top-right">
        <q-btn
          class="bg-white"
          icon="close"
          round
          dense
          style="z-index: 99"
          v-close-popup
        />
      </div>
      <q-card-section class="full-height q-pa-none">
        <q-img :src="previewImage" fit="contain" height="100%"></q-img
      ></q-card-section>
    </q-card>
  </q-dialog>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-pb-md">
      <div>
        <q-btn icon="arrow_back" size="sm" @click="$router.go(-1)">Назад</q-btn>
      </div>
      <div>
        <q-btn
          v-if="exists && storeAuth.hasPerm('recipes.add_ingredient')"
          icon="add"
          size="sm"
          color="positive"
          @click="$router.push({ name: 'ingredient', params: { id: 'new' } })"
          >Новый ингредиент</q-btn
        >
      </div>
    </div>
    <q-form
      class="q-my-md"
      @submit.prevent="saveIngredient()"
      v-if="ingredient"
    >
      <q-card padding>
        <q-card-section class="q-col-gutter-y-md">
          <!-- Main fields -->
          <q-input
            v-model="ingredient.title"
            label="Название ингредиента"
            :rules="[requiredRule]"
            :readonly="!canEdit"
            hide-bottom-space
            filled
          ></q-input>
          <q-select
            v-model.number="ingredient.category"
            @filter="filterCategories"
            :options="ingredientCategories || []"
            :input-debounce="0"
            :readonly="!canEdit"
            label="Категория"
            option-label="title"
            option-value="id"
            use-input
            map-options
            options-dense
            clearable
            filled
          >
          </q-select>
          <q-input
            v-model.number="ingredient.min_pack_size"
            :readonly="!canEdit"
            label="Размер упаковки"
            type="number"
            filled
          ></q-input>
          <q-input
            v-model.number="ingredient.item_weight"
            :readonly="!canEdit"
            label="Вес одной штуки"
            type="number"
            filled
          ></q-input>

          <q-input
            v-model.number="ingredient.price"
            :readonly="!canEdit"
            type="number"
            label="Цена (₺)"
            filled
          ></q-input>

          <q-input
            v-model="ingredient.description"
            :readonly="!canEdit"
            type="textarea"
            label="Описание"
            filled
            autogrow
          >
          </q-input>

          <!-- Image -->
          <div v-if="exists">
            <q-separator />
          </div>

          <div class="row q-col-gutter-y-md" v-if="exists">
            <div class="col-12 col-md-5 row">
              <div :class="$q.screen.gt.md ? 'col-6' : 'col-grow'">
                <q-file
                  v-model="uploadFile"
                  :readonly="!canEdit"
                  class="full-width"
                  ref="upload_field"
                  label="Загрузка изображения"
                  accept=".jpg, image/*"
                  dense
                  filled
                />
              </div>
              <div>
                <q-btn
                  @click="confirmClearImage()"
                  v-if="ingredient.image && canEdit"
                  align="left"
                  label="Очистить"
                  color="primary"
                  flat
                  no-caps
                ></q-btn>
              </div>
            </div>

            <div class="col-12 col-md-7 col-grow">
              <div v-if="previewImage">
                <q-img :src="previewImage" height="200px" fit="contain">
                  <div class="absolute-bottom-right bg-none">
                    <q-btn
                      push
                      round
                      dense
                      color="white"
                      text-color="primary"
                      :icon="imageFullscreen ? 'fullscreen_exit' : 'fullscreen'"
                      @click="imageFullscreen = !imageFullscreen"
                    />
                  </div>
                </q-img>
              </div>
            </div>
          </div>

          <!-- Toggle -->
          <div>
            <q-separator />
          </div>

          <div class="row">
            <q-toggle
              v-model="ingredient.need_buy"
              :readonly="!canEdit"
              label="Требует покупки"
            >
            </q-toggle>
            <q-toggle
              v-model="ingredient.edible"
              :readonly="!canEdit"
              label="Съедобный"
            >
            </q-toggle>
          </div>
        </q-card-section>

        <!-- Bottom actions -->
        <q-card-actions class="q-col-gutter-x-md q-mx-none q-pb-md">
          <div>
            <q-btn
              v-if="canEdit"
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
              v-if="exists && storeAuth.hasPerm('recipes.delete_ingredient')"
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
import { ingredientFromRead } from "src/Convert";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";
import { useAuthStore } from "src/stores/auth";
import { useBaseStore } from "src/stores/base";
import { defineComponent } from "vue";

const defaultIngredient = {
  title: "",
  description: "",
  need_buy: true,
  edible: true,
};

export default defineComponent({
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();

    return {
      store,
      storeAuth,
      loading: false,
      saving: false,
      deleting: false,
      searchCategory: "",
      uploadFile: null,
      uploadPreview: null as string | null,
      imageFullscreen: false,
      requiredRule: (val: string | number | undefined) =>
        !!val || "Обязательное поле",
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

      if (id == "new") {
        this.resetData();
        return;
      }

      if (typeof id == "string") {
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
          this.handleErrors(err, "Ошибка загрузки ингредиента");
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
          this.handleErrors(err, "Ошибка загрузки категорий ингредиентов");
        });
    },
    resetData() {
      // @ts-expect-error: Ingredient will be created
      this.store.ingredient = Object.assign({}, defaultIngredient);
    },
    filterCategories(search: string, update: CallableFunction) {
      this.searchCategory = search;
      update();
    },
    saveIngredient() {
      let payload = ingredientFromRead(this.ingredient);
      this.saving = true;

      let isCreating = !this.exists;
      let method = isCreating
        ? this.store.createIngredient
        : this.store.saveIngredient;

      // payload.category =
      //   typeof payload.category == 'number' ? payload.category : payload.category?.id;
      // if (!typeof payload.category == 'number') {
      //   payload.category = payload.category;
      // }
      if (isCreating) {
        payload.image = null;
      } else {
        if (!payload.image) {
          payload.image = "";
        }
      }
      console.debug("Payload: ", payload);
      method(payload)
        .then((resp) => {
          this.saving = false;

          if (isCreating) {
            void this.$router.replace({
              name: "ingredient",
              params: { id: resp.id },
            });
          }

          let created_tx = isCreating ? "создан" : "сохранен";
          this.$q.notify({
            type: "positive",
            message: `Ингредиент успешно ${created_tx}`,
          });
        })
        .catch((err: CustomAxiosError) => {
          this.saving = false;
          this.handleErrors(err, "Ошибка сохранения ингредиента");
        });
    },
    confirmClearImage() {
      if (!this.ingredient?.image) return;

      this.$q
        .dialog({
          title: "Подтверждение",
          message: `Вы уверены что хотите удалить изображение рецепта?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          if (!this.ingredient?.image) return;
          this.ingredient.image = null;
        });
    },
    askDelete() {
      this.$q
        .dialog({
          title: "Подтверждение",
          message:
            "Вы уверены что хотите удалить этот ингредиент? Он будет удален из всех используемых рецептов и из списка продуктов.",
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          void this.deleteIngredient().then(() => {
            this.$q.notify({
              type: "positive",
              message: `Ингредиент успешно удален`,
              icon: "delete",
            });
            void this.$router.replace({ name: "ingredients" });
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
            this.handleErrors(err, "Ошибка удаления ингредиента");
          });
      });
    },
  },
  computed: {
    ingredient() {
      return this.store.ingredient;
    },
    ingredientCategories() {
      if (this.searchCategory) {
        return (
          this.store.ingredient_categories?.filter(
            (c) => c.title.toLowerCase().indexOf(this.searchCategory) > -1
          ) || []
        );
      } else {
        return this.store.ingredient_categories;
      }
    },
    exists() {
      return Boolean(this.ingredient?.id);
    },
    previewImage() {
      return this.uploadPreview || this.ingredient?.image;
    },
    canEdit() {
      return this.storeAuth.hasPerm("recipes.change_ingredient");
    },
  },
  watch: {
    uploadFile(val: File | null) {
      if (!val) {
        return;
      }
      // @ts-expect-error: file will be converted on sending
      this.ingredient.image = val;
      this.uploadPreview = URL.createObjectURL(val);
    },
  },
});
</script>
