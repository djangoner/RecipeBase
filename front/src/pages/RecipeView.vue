<template>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-mb-md">
      <div>
        <q-btn icon="arrow_back" size="sm" @click="$router.go(-1)">Назад</q-btn>
      </div>
      <div v-if="!edit">
        <q-btn
          icon="add"
          size="sm"
          color="positive"
          @click="$router.push({ name: 'recipe', params: { id: 'new' } })"
          >Новый рецепт</q-btn
        >
      </div>
    </div>

    <q-form @submit.prevent="saveRecipe()">
      <div class="row q-gutter-y-lg q-col-gutter-x-md" v-if="recipe">
        <div class="col-xs-12 col-md-6">
          <!--  col-lg-8 -->
          <q-card>
            <q-card-section>
              <!-- Recipe details -->
              <div class="q-mt-none q-mb-md">
                <q-input
                  v-model="recipe.title"
                  v-if="edit"
                  label="Название рецепта *"
                  :rules="[requiredRule]"
                  filled
                >
                  <template #after>
                    <q-btn v-if="exists" icon="edit" @click="toggleEdit()" flat>
                      <q-tooltip
                        >Предпросмотр рецепта (изменения не будут применены!)</q-tooltip
                      >
                    </q-btn>
                  </template></q-input
                >
                <h4 class="text-center q-my-none" v-else>
                  {{ recipe.title }}
                  <q-btn icon="edit" @click="toggleEdit()" flat>
                    <q-tooltip>Изменить рецепт</q-tooltip>
                  </q-btn>
                </h4>
              </div>

              <!-- Recipe source -->
              <div class="q-my-md">
                <q-input
                  v-model="recipe.source_link"
                  v-if="edit"
                  label="Источник рецепта"
                  filled
                >
                </q-input>
                <h6 class="text-center q-my-none" v-else>
                  <q-btn
                    v-if="recipe.source_link && recipe.source_link.startsWith('http')"
                    :href="recipe.source_link"
                    target="_blank"
                    icon="open_in_new"
                    size="sm"
                    >Открыть источник</q-btn
                  >
                  <h6 class="text-center q-my-none" v-else>
                    Источник: {{ recipe.source_link || '-' }}
                  </h6>
                </h6>
              </div>

              <!-- Recipe tags -->
              <div class="row recipe-tags items-center q-gutter-x-md">
                <span class="text-subtitle2">Метки: </span>
                <q-chip
                  class="cursor-pointer"
                  v-for="tag of recipe.tags"
                  :key="tag.id"
                  :removable="edit"
                  @remove="removeTag(tag)"
                >
                  {{ tag.title }}
                </q-chip>

                <q-select
                  v-model="tagAddSelect"
                  v-if="edit && tags"
                  label="Добавить метку"
                  keydown.enter.prevent="addTag()"
                  @filter="filterTags"
                  :input-debounce="0"
                  :options="tagList"
                  option-label="title"
                  use-input
                  options-dense
                  dense
                  @new-value="addTag"
                >
                  <template v-slot:no-option>
                    <q-item>
                      <q-item-section class="text-grey"> Нет результатов </q-item-section>
                    </q-item>
                  </template>
                  <template #after>
                    <q-btn
                      @click="addTag()"
                      icon="add"
                      size="sm"
                      color="positive"
                    ></q-btn>
                  </template>
                </q-select>
              </div>

              <!-- Info -->

              <div class="q-my-md">
                <q-input
                  v-if="edit"
                  v-model.number="recipe.portion_count"
                  type="number"
                  label="Количество порций"
                  filled
                >
                </q-input>
                <h6 class="text-center q-my-none" v-else-if="recipe.portion_count">
                  <q-icon name="pie_chart_outline" color="grey"></q-icon>
                  Порций: {{ recipe.portion_count || '-' }}
                </h6>
              </div>
              <div class="q-my-md">
                <q-input
                  v-if="edit"
                  v-model.number="recipe.cooking_time"
                  type="number"
                  label="Время приготовления"
                  hint="Примерное время приготовления в минутах"
                  filled
                >
                </q-input>
                <h6 class="text-center q-my-none" v-else-if="recipe.cooking_time">
                  <q-icon name="timer" color="grey"></q-icon>
                  Время приготовления: {{ recipe.cooking_time || '-' }}
                </h6>
              </div>

              <!-- Images carousel -->
              <div class="images-carousel q-pa-md" v-if="!edit">
                <q-carousel
                  animated
                  v-model="slide"
                  v-model:fullscreen="fullscreen"
                  navigation
                  infinite
                  :autoplay="autoplay"
                  arrows
                  transition-prev="slide-right"
                  transition-next="slide-left"
                  height="250px"
                  @mouseenter="autoplay = false"
                  @mouseleave="autoplay = true"
                  v-if="recipe.images?.length > 0"
                >
                  <template v-slot:control>
                    <q-carousel-control position="bottom-right" :offset="[18, 18]">
                      <q-btn
                        push
                        round
                        dense
                        color="white"
                        text-color="primary"
                        :icon="fullscreen ? 'fullscreen_exit' : 'fullscreen'"
                        @click="fullscreen = !fullscreen"
                      />
                    </q-carousel-control>
                  </template>
                  <q-carousel-slide
                    :name="idx + 1"
                    :img-src="img.image"
                    v-for="(img, idx) of recipe.images"
                    :key="img.id"
                  />
                </q-carousel>
              </div>

              <recipe-images-upload
                v-model="recipe.images"
                v-if="edit && exists"
              ></recipe-images-upload>
              <q-separator />

              <!-- Recipe content -->

              <div class="q-pa-md q-gutter-sm" v-if="edit">
                <q-input
                  v-model="recipe.short_description"
                  type="textarea"
                  label="Короткое описание"
                  hint="Показывается на карточке рецепта"
                  :disable="!edit"
                />

                <h6 class="q-my-sm">Содержание (изначальное, источник)</h6>
                <q-editor
                  v-model="recipe.content_source"
                  :dense="$q.screen.lt.md"
                  :toolbar="editorToolbar"
                  :fonts="editorFonts"
                />
                <h6 class="q-my-sm">Содержание (редактированное)</h6>
                <q-editor
                  v-model="recipe.content"
                  :dense="$q.screen.lt.md"
                  :toolbar="editorToolbar"
                  :fonts="editorFonts"
                />

                <h6 class="q-my-sm">Комментарий</h6>
                <q-input v-model="recipe.comment" type="textarea" label="Комментарий" />
              </div>
              <div v-else>
                <div class="q-my-md" v-if="recipe.content_source">
                  <span class="text-h6 q-my-sm text-primary"
                    >Содержание (изначальное)</span
                  >
                  <div class="recipe-text" v-html="recipe.content_source"></div>
                  <q-separator />
                </div>

                <div class="q-my-md" v-if="recipe.content">
                  <span class="text-h6 q-my-sm text-primary">Содержание</span>

                  <div class="recipe-text" v-html="recipe.content"></div>
                  <q-separator />
                </div>
                <div class="q-my-md" v-if="recipe.comment">
                  <span class="text-h6 q-my-sm text-primary">Комментарий</span>

                  <div class="recipe-text format-spaces" v-html="recipe.comment"></div>
                  <q-separator />
                </div>
              </div>

              <div class="flex justify-around">
                <q-btn
                  @click="saveAndContinue = false"
                  type="submit"
                  icon="save"
                  color="positive"
                  :loading="saving"
                  v-if="edit"
                  >Сохранить</q-btn
                >
                <q-btn
                  @click="saveAndContinue = true"
                  type="submit"
                  icon="save"
                  color="positive"
                  :loading="saving"
                  v-if="edit"
                  >Сохранить и продолжить</q-btn
                >
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-xs-12 col-md-6 q-gutter-y-sm">
          <!--  col-lg-4 -->
          <!-- Aside information -->
          <q-card class="q-mt-none position-sticky">
            <q-card-section>
              <!-- Info -->
              <q-expansion-item label="Подробности">
                <div class="row column q-px-md q-col-gutter-sm">
                  <span><b>Дата создания:</b> {{ dateFormat(recipe.created) }}</span>
                  <span><b>Дата изменения:</b> {{ dateFormat(recipe.edited) }}</span>
                  <span><b>Автор:</b> {{ recipe?.author?.username || '?' }}</span>
                </div>
              </q-expansion-item>
              <!-- Ingredients -->
              <div class="q-my-sm">
                <div class="text-h6 text-center q-mb-sm">Игредиенты:</div>

                <q-table
                  class="no-bottom"
                  :rows="recipe.ingredients"
                  :columns="ingredientsColumns"
                  :rows-per-page-options="[0]"
                  :hide-pagination="true"
                  flat
                  dense
                  v-if="recipe?.ingredients?.length > 0 || edit"
                >
                  <template #bottom> </template>
                  <!-- Custom fields -->

                  <template #body-cell-title="slotScope">
                    <td class="text-right" style="width: 50px">
                      <q-select
                        v-model="slotScope.row.ingredient"
                        v-if="edit"
                        :input-debounce="0"
                        :options="ingList"
                        option-label="title"
                        style="max-width: 120px"
                        @filter="filterIngredients"
                        @new-value="addIngredient"
                        use-input
                        options-dense
                        dense
                      >
                        <template v-slot:no-option>
                          <q-item>
                            <q-item-section class="text-grey">
                              Нет результатов
                            </q-item-section>
                          </q-item>
                        </template>
                      </q-select>
                      <span v-else>{{ slotScope.value }}</span>
                    </td>
                  </template>

                  <template #body-cell-amount_rec="slotScope">
                    <td class="text-right" style="width: 50px">
                      <q-input
                        v-if="edit"
                        v-model.number="slotScope.row.amount"
                        type="number"
                        step="0.01"
                        dense
                      >
                        <q-tooltip>
                          Единица измерения: {{ slotScope.row.amount_type_str }}
                        </q-tooltip>
                      </q-input>
                      <span v-else>{{ slotScope.value }}</span>
                    </td>
                  </template>

                  <template #body-cell-is_main="slotScope">
                    <td class="text-right" style="width: 30px">
                      <q-checkbox
                        v-model="slotScope.row.is_main"
                        :disable="!edit"
                        size="sm"
                      ></q-checkbox>
                    </td>
                  </template>

                  <!-- Bottom row -->
                  <template v-if="edit" v-slot:body-cell-actions="slotProps">
                    <q-td class="q-py-none">
                      <div class="row justify-around">
                        <q-btn
                          icon="delete"
                          color="negative"
                          size="xs"
                          dense
                          @click="removeIngredient(slotProps.row)"
                        ></q-btn>
                      </div>
                    </q-td>
                  </template>
                  <template v-if="edit" #bottom-row>
                    <q-tr>
                      <q-td>
                        <q-select
                          v-model="ingAdd.select"
                          v-if="edit"
                          label="Ингредиент"
                          :input-debounce="0"
                          :options="ingList"
                          option-label="title"
                          style="max-width: 120px"
                          @keydown.enter.prevent="addIngredient()"
                          @filter="filterIngredients"
                          @new-value="addIngredient"
                          options-dense
                          use-input
                          dense
                        >
                          <template v-slot:no-option>
                            <q-item>
                              <q-item-section class="text-grey">
                                Нет результатов
                              </q-item-section>
                            </q-item>
                          </template>
                        </q-select>
                      </q-td>
                      <q-td>
                        <q-input
                          v-model.number="ingAdd.amount"
                          type="number"
                          label="Вес"
                          step="0.1"
                        ></q-input>
                      </q-td>
                      <q-td>
                        <q-select
                          v-model="ingAdd.amount_type"
                          v-if="edit"
                          use-input
                          @keydown.enter.prevent="addIngredient()"
                          @filter="filterIngredientsAmountType"
                          :input-debounce="0"
                          :options="amountTypeList"
                          option-label="title"
                          option-value="id"
                          map-options
                          emit-value
                          options-dense
                          dense
                          style="max-width: 100px"
                        >
                          <template v-slot:no-option>
                            <q-item>
                              <q-item-section class="text-grey">
                                Нет результатов
                              </q-item-section>
                            </q-item>
                          </template>
                        </q-select>
                      </q-td>

                      <q-td>
                        <div class="flex justify-center items-center">
                          <q-btn
                            color="positive"
                            icon="add"
                            size="sm"
                            @click="addIngredient()"
                          ></q-btn>
                        </div>
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>

                <div
                  class="flex justify-center items-center"
                  style="height: 100px"
                  v-else
                >
                  <h6 class="text-bold">Игредиенты не указаны</h6>
                </div>
              </div>

              <!-- Recipe Ratings -->

              <div class="q-my-sm">
                <div class="text-h6 text-center q-mb-sm">Рейтинг:</div>

                <recipe-rating v-model="store.recipe" :edit="edit"></recipe-rating>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-form>

    <q-inner-loading :showing="loading || saving"></q-inner-loading>
  </q-page>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';
import RecipeImagesUpload from 'src/components/RecipeImagesUpload.vue';
import recipeRating from 'src/components/RecipeRating.vue';

let defaultRecipe = {
  content: '',
  tags: [],
  images: [],
  ingredients: [],
  ratings: [],
};

export default {
  components: {
    RecipeImagesUpload,
    recipeRating,
  },
  data() {
    const store = useBaseStore();

    let ingredientsColumns = [
      {
        name: 'title',
        label: 'Название',
        field: (row) => row.ingredient.title,
        required: true,
        sortable: true,
        style: 'width: 50px',
      },
      // {
      //   name: 'amount_type',
      //   label: 'Ед. изм.',
      //   field: (row) => row.amount_type,
      //   required: true,
      //   sortable: true,
      //   style: 'width: 20px',
      // },
      {
        name: 'amount_rec',
        label: 'Вес (рецепт)',
        field: (row) => row.amount + '  (' + row.amount_type_str + ')',
        required: true,
        sortable: true,
        style: 'width: 20px',
      },
      {
        name: 'amount_g',
        label: 'Вес (гр.)',
        field: (row) => (row.amount_grams ? row.amount_grams + ' гр.' : '-'),
        required: true,
        sortable: true,
        style: 'width: 30px',
      },
      {
        name: 'is_main',
        label: 'Основной',
        field: 'is_main',
        required: true,
        sortable: true,
        style: 'width: 30px',
      },
    ];

    let ingAddDefault = {
      select: null,
      amount: null,
      amount_type: 'g',
      is_main: false,
    };

    let editorToolbar = [
      [
        {
          label: this.$q.lang.editor.align,
          icon: this.$q.iconSet.editor.align,
          fixedLabel: true,
          list: 'only-icons',
          options: ['left', 'center', 'right', 'justify'],
        },
        {
          label: this.$q.lang.editor.align,
          icon: this.$q.iconSet.editor.align,
          fixedLabel: true,
          options: ['left', 'center', 'right', 'justify'],
        },
      ],
      ['bold', 'italic', 'strike', 'underline', 'subscript', 'superscript'],
      ['token', 'hr', 'link', 'custom_btn'],
      ['print', 'fullscreen'],
      [
        {
          label: this.$q.lang.editor.formatting,
          icon: this.$q.iconSet.editor.formatting,
          list: 'no-icons',
          options: ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code'],
        },
        {
          label: this.$q.lang.editor.fontSize,
          icon: this.$q.iconSet.editor.fontSize,
          fixedLabel: true,
          fixedIcon: true,
          list: 'no-icons',
          options: ['size-1', 'size-2', 'size-3', 'size-4', 'size-5', 'size-6', 'size-7'],
        },
        {
          label: this.$q.lang.editor.defaultFont,
          icon: this.$q.iconSet.editor.font,
          fixedIcon: true,
          fixedIcon: true,
          list: 'no-icons',
          options: [
            'default_font',
            'arial',
            'arial_black',
            'comic_sans',
            'courier_new',
            'impact',
            'lucida_grande',
            'times_new_roman',
            'verdana',
          ],
        },
        'removeFormat',
      ],
      ['quote', 'unordered', 'ordered', 'outdent', 'indent'],

      ['undo', 'redo'],
      ['viewsource'],
    ];

    let editorFonts = {
      arial: 'Arial',
      arial_black: 'Arial Black',
      comic_sans: 'Comic Sans MS',
      courier_new: 'Courier New',
      impact: 'Impact',
      lucida_grande: 'Lucida Grande',
      times_new_roman: 'Times New Roman',
      verdana: 'Verdana',
    };

    let requiredRule = (val) => !!val || 'Обязательное поле';

    return {
      store,
      loading: false,
      saving: false,
      slide: 1,
      autoplay: true,
      fullscreen: false,
      edit: false,
      tagAddSelect: null,
      tagList: null,
      amountTypeList: null,
      saveAndContinue: false,
      ingAddDefault,
      ingAdd: Object.assign({}, ingAddDefault),
      ingList: null,
      requiredRule,
      ingredientsColumns,
      editorToolbar,
      editorFonts,
    };
  },
  mounted() {
    this.loadRecipe();
    if (!this.tags) {
      this.loadTags();
    }
    if (!this.ingredients) {
      this.loadIngredients();
    }
    if (!this.amount_types) {
      this.loadAmountTypes();
    }
  },
  beforeRouteUpdate(to) {
    this.loadRecipe(to.params.id);
  },
  methods: {
    loadRecipe(load_id) {
      let id = load_id || this.$route.params.id;

      if (id == 'new') {
        this.resetData();
        this.edit = true;
        return;
      }

      let payload = {
        id: id,
      };
      this.loading = true;

      this.store
        .loadRecipe(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки рецептов');
        });
    },
    resetData() {
      console.debug('Recipe resetData');
      this.store.recipe = Object.assign({}, defaultRecipe);
      // this.recipe = Object.assign({}, defaultRecipe);
      this.recipe.tags.length = 0;
      this.recipe.ingredients.length = 0;
    },
    async uploadImg(img) {
      return new Promise((resolve, reject) => {
        let formData = new FormData();
        formData.append('recipe', this.recipe.id);
        formData.append('image', img.image);
        formData.append('title', img.title);
        formData.append('num', img.num);

        this.store
          .createRecipeImage(formData)
          .then((resp) => {
            resolve(resp.data);
            console.debug('IMG: ', resp);
          })
          .catch((err) => reject(err));
      });
    },
    async handleImages(payload) {
      payload.images = await Promise.all(
        payload.images.map(async (i) => {
          // console.debug('Image upload: ', i, Boolean(i.upload_preview), Boolean(i.id));
          if (i.upload_preview) {
            let res = await this.uploadImg(i);
            // (async () => {
            // await ...
            // })();
            console.debug('IMG uploaded: ', res, i);

            Object.assign(i, res);
            // delete res['image'];
          }
          if (i.id) {
            delete i['image'];
          }
          return i;
        })
      );
      return payload;
    },
    async saveRecipe() {
      // console.debug('Save recipe');
      this.saving = true;
      if (!this.saveAndContinue) {
        this.edit = false;
      }

      let payload = Object.assign({}, this.recipe);
      let isCreating = !this.exists;
      let method = isCreating ? this.store.createRecipe : this.store.saveRecipe;

      if (isCreating) {
        payload.images = [];
      } else {
        payload = await this.handleImages(payload);
      }

      if (!payload.cooking_time) {
        payload.cooking_time = 0;
      }
      if (!payload.portion_count) {
        payload.portion_count = 0;
      }

      payload.ratings = payload.ratings.map((r) => {
        if (r.user) {
          r.user = r.user.id;
        }
        return r;
      });

      console.debug('Saving recipe: ', payload);

      method(payload)
        .then((resp) => {
          this.saving = false;

          if (isCreating) {
            console.debug('Redirecting from created recipe: ', resp.data);
            this.$router.push({ name: 'recipe', params: { id: resp.data.id } });
            // .catch(() => {});
          }

          let created_tx = isCreating ? 'создан' : 'сохранен';
          this.$q.notify({
            type: 'positive',
            message: `Рецепт успешно ${created_tx}`,
          });
          this.loadIngredients();
        })
        .catch((err) => {
          this.saving = false;
          this.edit = true;
          this.handleErrors(err, 'Ошибка сохранения рецепта');
        });
    },
    loadTags() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadTags(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки меток');
        });
    },
    loadIngredients() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadIngredients(payload)
        .then(() => {
          this.ingList = this.ingredients?.results;
          // this.loading = false;
        })
        .catch((err) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    loadAmountTypes() {
      let payload = {
        page_size: 1000,
      };
      this.store
        .loadAmountTypes(payload)
        .then(() => {
          // this.loading = false;
          this.amountTypeList = this.amount_types?.types;
        })
        .catch((err) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки типов измерений');
        });
    },
    toggleEdit() {
      this.edit = !this.edit;
    },
    removeTag(tag) {
      console.debug('Remove tag: ', tag);
      this.recipe.tags = this.recipe.tags.filter((t) => {
        return t.title !== tag.title;
      });
    },
    addTag(new_tag, done) {
      if (new_tag) {
        this.tagAddSelect = {
          id: null,
          title: new_tag,
        };
        // done(new_tag);
        // return;
      }
      console.debug('Add tag: ', this.tagAddSelect, new_tag);
      if (!this.tagAddSelect) {
        return;
      }
      this.recipe.tags.push(this.tagAddSelect);
      this.tagAddSelect = null;
    },
    filterTags(val, update, abort) {
      update(() => {
        let isUsed = (tag) => {
          return this.recipe.tags.some((t) => t.id == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags?.results;

        this.tagList = tags?.filter(
          (v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)
        );
        // console.debug(needle, this.tagList, tags);
      });
    },
    addIngredient(new_val) {
      if (new_val) {
        this.ingAdd.select = {
          id: null,
          title: new_val,
        };
        // done(new_val);
        return;
      }
      console.debug('Add ingredient: ', this.ingAdd, new_val);
      if (!this.ingAdd.select || !this.ingAdd.amount || !this.ingAdd.amount_type) {
        return;
      }
      this.recipe.ingredients.push({
        ingredient: this.ingAdd.select,
        amount: this.ingAdd.amount,
        amount_type: this.ingAdd.amount_type,
        is_main: false,
      });
      this.ingAdd = Object.assign({}, this.ingAddDefault);
    },

    removeIngredient(row) {
      console.debug('Remove ingredient: ', row);
      this.$q
        .dialog({
          title: 'Подтверждение удаления ингредиента',
          message: `Вы уверены что хотите удалить ингредиент '${row.ingredient.title}' ?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          console.debug('Remove ingredient confirmed');
          this.recipe.ingredients = this.recipe.ingredients.filter((t) => {
            return t != row;
          });
        });
    },

    filterIngredients(val, update, abort) {
      update(() => {
        let isUsed = (ing) => {
          // console.debug(ing, this.recipe.ingredients);
          return this.recipe.ingredients.some((t) => t.ingredient.id == ing.id);
        };
        const needle = val.toLowerCase();
        let ingredients = this.ingredients?.results;

        this.ingList = ingredients?.filter(
          (v) => v.title.toLowerCase().indexOf(needle) > -1 // && !isUsed(v)
        );
        // console.debug(needle, this.tagList, tags);
      });
    },

    filterIngredientsAmountType(val, update, abort) {
      update(() => {
        const needle = val.toLowerCase();
        let amount_types = this.amount_types?.types;

        this.amountTypeList = amount_types?.filter(
          (v) => v.title.toLowerCase().indexOf(needle) > -1
        );
        // console.debug(needle, this.tagList, tags);
      });
    },
    dateFormat(raw) {
      return date.formatDate(raw, 'YYYY.MM.DD HH:MM');
    },
  },

  computed: {
    recipe() {
      return this.store.recipe;
    },
    tags() {
      return this.store.tags;
    },
    ingredients() {
      return this.store.ingredients;
    },
    amount_types() {
      return this.store.amount_types;
    },
    exists() {
      return Boolean(this.recipe?.id);
    },
  },

  watch: {
    edit(val) {
      let column_actions = {
        name: 'actions',
        label: 'Действия',
        required: true,
        sortable: true,
      };

      if (val) {
        this.ingredientsColumns.push(column_actions);
      } else {
        this.ingredientsColumns.pop(column_actions);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.position-sticky {
  position: sticky;
  top: 60px;
}

:deep(.recipe-text) {
  overflow: hidden;

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 120%;
  }
  h1 {
    font-size: 2.5rem;
    font-weight: bold;
  }
  h2 {
    font-size: 2rem;
    font-weight: bold;
  }
  h3 {
    font-size: 1.5rem;
  }
  h4,
  h5,
  h6 {
    font-size: 1rem;
  }

  img {
    max-width: 100%;
  }
}
.format-spaces {
  white-space: pre-line;
}
:deep(.no-bottom) {
  .q-table__bottom {
    display: none;
    min-height: 0;
  }
}
</style>
