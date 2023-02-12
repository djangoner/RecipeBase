<template>
  <q-page padding>
    <div class="row q-col-gutter-x-md q-pb-md">
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

    <q-form class="q-mt-md" @submit.prevent="saveRecipe()">
      <div class="row q-gutter-y-lg q-col-gutter-x-md" v-if="recipe">
        <div class="col-xs-12 col-md-6">
          <!--  col-lg-8 -->
          <q-card>
            <q-card-section
              class="flex column"
              :class="dense ? 'q-gutter-y-sm' : 'q-gutter-y-md'"
            >
              <!-- Recipe details -->
              <div class="q-mt-none">
                <q-input
                  v-model="recipe.title"
                  v-if="edit"
                  label="Название рецепта *"
                  :rules="[requiredRule]"
                  filled
                  :dense="dense"
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
                  <q-icon
                    v-if="recipe.is_archived"
                    class="q-mr-xs"
                    name="archive"
                    size="sm"
                    color="primary"
                  >
                    <q-tooltip>Этот рецепт архивирован</q-tooltip>
                  </q-icon>
                  {{ recipe.title }}
                  <q-btn icon="edit" @click="toggleEdit()" flat>
                    <q-tooltip>Изменить рецепт</q-tooltip>
                  </q-btn>

                  <recipe-menu :recipe="recipe" />
                </h4>
              </div>

              <!-- Recipe source -->
              <div>
                <q-input
                  v-model="recipe.source_link"
                  v-if="edit"
                  label="Источник рецепта"
                  filled
                  :dense="dense"
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
                  @filter="filterTags"
                  @new-value="addNewTag"
                  keydown.enter.prevent="addTag()"
                  :input-debounce="0"
                  :options="tagList || []"
                  :options-dense="dense"
                  :dense="dense"
                  option-label="title"
                  use-input
                  new-value-mode="add-unique"
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

              <div>
                <q-input
                  v-if="edit"
                  v-model.number="recipe.portion_count"
                  type="number"
                  label="Количество порций"
                  filled
                  :dense="dense"
                >
                </q-input>
                <h6 class="text-center q-my-none" v-else-if="recipe.portion_count">
                  <q-icon name="pie_chart_outline" color="grey"></q-icon>
                  Порций: {{ recipe.portion_count || '-' }}
                </h6>
              </div>
              <div>
                <q-input
                  v-if="edit"
                  v-model.number="recipe.cooking_time"
                  type="number"
                  label="Время приготовления"
                  hint="Примерное время приготовления в минутах"
                  filled
                  :dense="dense"
                >
                </q-input>
                <h6 class="text-center q-my-none" v-else-if="recipe.cooking_time">
                  <q-icon name="timer" color="grey"></q-icon>
                  Время приготовления: {{ recipe.cooking_time || '-' }}
                </h6>
              </div>
              <div v-if="edit">
                <q-select
                  v-model="recipe.is_archived"
                  :options="archivedOptions"
                  label="Статус"
                  options-dense
                  map-options
                  emit-value
                  filled
                  :dense="dense"
                ></q-select>
              </div>

              <!-- Images carousel -->
              <div class="images-carousel q-py-md" v-if="!edit">
                <q-carousel
                  v-if="(recipe.images || [])?.length > 0"
                  v-model="slide"
                  v-model:fullscreen="fullscreen"
                  @mouseenter="autoplay = false"
                  @mouseleave="autoplay = true"
                  :autoplay="autoplay"
                  :height="$q.screen.gt.md ? '450px' : '250px'"
                  transition-prev="slide-right"
                  transition-next="slide-left"
                  animated
                  navigation
                  infinite
                  arrows
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

              <div class="q-py-md q-gutter-sm full-width" v-if="edit">
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
                <div v-if="recipe.content_source">
                  <span class="text-h6 q-my-sm text-primary"
                    >Содержание (изначальное)</span
                  >
                  <div class="recipe-text" v-html="recipe.content_source"></div>
                  <q-separator />
                </div>

                <div v-if="recipe.content">
                  <span class="text-h6 q-my-sm text-primary">Содержание</span>

                  <div class="recipe-text" v-html="recipe.content"></div>
                  <q-separator />
                </div>
              </div>
              <q-input
                v-model="recipe.short_description"
                type="textarea"
                label="Короткое описание"
                hint="Показывается на карточке рецепта"
                :readonly="!edit"
              />
              <div v-if="!edit && recipe.comment">
                <span class="text-h6 q-my-sm text-primary">Комментарий</span>

                <div class="recipe-text format-spaces" v-html="recipe.comment"></div>
                <q-separator />
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
        <div class="col-xs-12 col-md-6 q-mt-sm q-gutter-y-sm">
          <!--  col-lg-4 -->
          <!-- Aside information -->
          <q-card class="q-mt-none position-sticky">
            <q-card-section>
              <!-- Info -->
              <q-expansion-item label="Подробности">
                <div class="row column q-px-md q-col-gutter-sm">
                  <span><b>Дата создания:</b> {{ dateTimeFormat(recipe.created) }}</span>
                  <span><b>Дата изменения:</b> {{ dateTimeFormat(recipe.edited) }}</span>
                  <span v-if="recipe.last_cooked"
                    ><b>Последний раз приготовлено:</b>
                    {{ dateFormat(recipe.last_cooked) }}</span
                  >
                  <span v-if="recipe.cooked_times"
                    ><b>Приготовлено (раз):</b> {{ recipe.cooked_times }}</span
                  >
                  <span><b>Автор:</b> {{ recipe?.author?.username || '?' }}</span>
                </div>
              </q-expansion-item>
              <q-expansion-item label="Цены">
                <q-markup-table flat>
                  <thead>
                    <tr>
                      <th class="text-right">Название</th>
                      <th class="text-right">Цена (необх.)</th>
                      <th class="text-right">Цена (полная)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ing of recipe.ingredients" :key="ing.id">
                      <td class="text-right">{{ ing.ingredient.title }}</td>
                      <td class="text-right">
                        {{ ing.price_part ? ing.price_part + '₺' : '-' }}
                      </td>
                      <td class="text-right">
                        {{ ing.price_full ? ing.price_full + '₺' : '-' }}
                      </td>
                    </tr>
                    <tr>
                      <td class="text-right">
                        <b>Итого</b>
                      </td>
                      <td class="text-right">{{ pricesPart || '0' }}₺</td>
                      <td class="text-right">{{ pricesFull || '0' }}₺</td>
                    </tr>
                  </tbody>
                </q-markup-table>
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
                  v-if="(recipe?.ingredients || [])?.length > 0 || edit"
                >
                  <template #bottom> </template>
                  <!-- Custom fields -->

                  <template #body-cell-title="slotScope">
                    <td class="text-right" style="width: 50px">
                      <q-select
                        v-model="slotScope.row.ingredient"
                        v-if="edit"
                        :input-debounce="0"
                        :options="ingList || []"
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
                          :options="ingList || []"
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
                          :options="amountTypeList || []"
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

                <recipe-rating
                  v-model="store.recipe"
                  :edit="edit"
                  v-if="store.recipe"
                ></recipe-rating>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-form>

    <q-inner-loading :showing="loading || saving"></q-inner-loading>
  </q-page>
</template>

<script lang="ts">
import { useBaseStore } from 'src/stores/base';
import { date } from 'quasar';
import RecipeImagesUpload from 'src/components/RecipeImagesUpload.vue';
import recipeRating from 'src/components/RecipeRating.vue';
import RecipeMenu from 'src/components/RecipeMenu.vue';
import { defineComponent } from 'vue';
import {
  AmountTypeEnum,
  IngredientRead,
  RecipeImage,
  RecipeIngredientRead,
  RecipeRead,
  RecipeTag,
} from 'src/client';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { AmountTypesTypes } from 'src/modules/Globals';
import { RecipeFromRead } from 'src/Convert';

let defaultRecipe = {
  content_source: '',
  content: '',
  tags: [],
  images: [],
  ingredients: [],
  ratings: [],
  portion_count: null,
};

interface PatchedRecipeRead {
  content: string;
  content_source: string;
  images: RecipeImage[];
}

export default defineComponent({
  components: {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeImagesUpload,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    recipeRating,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    RecipeMenu,
  },
  mixins: [HandleErrorsMixin],
  data() {
    const store = useBaseStore();

    let ingredientsColumns = [
      {
        name: 'title',
        label: 'Название',
        field: (row: RecipeIngredientRead) => row.ingredient.title,
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
        field: (row: RecipeIngredientRead) =>
          String(row.amount) + '  (' + row.amount_type_str + ')',
        required: true,
        sortable: true,
        style: 'width: 20px',
      },
      {
        name: 'amount_g',
        label: 'Вес (гр.)',
        field: (row: RecipeIngredientRead) =>
          row.amount_grams ? String(row.amount_grams) + ' гр.' : '-',
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
      select: null as { id: number | null; title: string } | null,
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

    let requiredRule = (val: string | number) => !!val || 'Обязательное поле';

    return {
      store,
      loading: false,
      saving: false,
      slide: 1,
      autoplay: true,
      fullscreen: false,
      edit: false,
      tagAddSelect: null as RecipeTag | null,
      tagList: null as RecipeTag[] | null,
      amountTypeList: null as AmountTypesTypes | null,
      saveAndContinue: false,
      ingAddDefault,
      ingAdd: Object.assign({}, ingAddDefault),
      ingList: null as IngredientRead[] | null,
      requiredRule,
      ingredientsColumns,
      editorToolbar,
      editorFonts,
      archivedOptions: [
        { label: 'Не архивирован', value: false },
        { label: 'Архивирован', value: true },
      ],
    };
  },
  mounted() {
    this.loadRecipe();
    if (!this.tags) {
      this.loadTags();
    }
    if (!this.ingredients || this.store.ingredients_searched) {
      this.loadIngredients();
    }
    if (!this.amount_types) {
      this.loadAmountTypes();
    }
  },
  beforeRouteUpdate(to) {
    if (to.params.id == 'new') {
      this.loadRecipe('new');
    } else {
      this.loadRecipe(parseInt(to.params?.id as string));
    }
  },
  methods: {
    loadRecipe(load_id?: number | 'new' | undefined) {
      let id: string | number | 'new' = load_id || (this.$route.params.id as string);

      if (id == 'new') {
        this.resetData();
        this.edit = true;
        return;
      } else {
        this.edit = false;
      }

      if (typeof id == 'string') {
        id = parseInt(id);
      }

      this.loading = true;

      this.store
        .loadRecipe(id)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки рецептов');
        });
    },
    resetData() {
      console.debug('Recipe resetData');
      // @ts-expect-error: Default recipe not full
      this.store.recipe = Object.assign({}, defaultRecipe);
      // this.recipe = Object.assign({}, defaultRecipe);
      if (this.recipe?.tags) {
        this.recipe.tags.length = 0;
      }
      if (this.recipe?.ingredients) {
        this.recipe.ingredients.length = 0;
      }
    },
    async uploadImg(img: RecipeImage): Promise<RecipeImage> {
      return new Promise((resolve, reject) => {
        if (!this.recipe) {
          reject();
        }
        // let formData = new FormData();
        // formData.append('recipe', String(this.recipe?.id as number));
        // formData.append('image', img.image);
        // formData.append('title', img.title as string);
        // formData.append('num', String(img.num));
        let payload = {
          recipe: String(this.recipe?.id as number),
          image: img.image,
          title: img.title as string,
          num: String(img.num),
        };

        this.store
          // @ts-expect-error: Recipe image will be created
          .createRecipeImage(payload)
          .then((resp) => {
            resolve(resp);
            console.debug('IMG: ', resp);
          })
          .catch((err) => reject(err));
      });
    },
    async handleImages(images_src: RecipeImage[]) {
      let images = await Promise.all(
        images_src.map(async (i) => {
          // console.debug('Image upload: ', i, Boolean(i.upload_preview), Boolean(i.id));
          // @ts-expect-error: Upload preview generation
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
            // @ts-expect-error readonly image
            delete i['image'];
          }
          return i;
        })
      );
      return images;
    },
    async saveRecipe() {
      // console.debug('Save recipe');
      this.saving = true;
      if (!this.saveAndContinue) {
        this.edit = false;
      }
      let payload = RecipeFromRead(this.recipe);
      let isCreating = !this.exists;
      let method = isCreating ? this.store.createRecipe : this.store.saveRecipe;

      if (isCreating) {
        payload.images = [];
      } else {
        payload.images = await this.handleImages(payload.images as RecipeImage[]);
      }

      console.debug('Saving recipe: ', payload);

      method(payload)
        .then((resp) => {
          this.saving = false;

          if (isCreating) {
            console.debug('Redirecting from created recipe: ', resp);
            void this.$router.replace({ name: 'recipe', params: { id: resp.id } });
            // .catch(() => {});
          }

          let created_tx = isCreating ? 'создан' : 'сохранен';
          this.$q.notify({
            type: 'positive',
            message: `Рецепт успешно ${created_tx}`,
          });
          // this.loadIngredients();
        })
        .catch((err: CustomAxiosError) => {
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
        .catch((err: CustomAxiosError) => {
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
          this.ingList = this.ingredients;
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки ингредиентов');
        });
    },
    loadAmountTypes() {
      this.store
        .loadAmountTypes()
        .then(() => {
          // this.loading = false;
          this.amountTypeList = this.amount_types?.types as AmountTypesTypes;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки типов измерений');
        });
    },
    toggleEdit() {
      this.edit = !this.edit;
    },
    removeTag(tag: RecipeTag) {
      if (!this.recipe) {
        return;
      }
      console.debug('Remove tag: ', tag);
      this.recipe.tags =
        this.recipe?.tags?.filter((t) => {
          return t.title !== tag.title;
        }) || [];
    },
    addTag() {
      console.debug('Add tag: ', this.tagAddSelect);
      if (!this.tagAddSelect) {
        return;
      }
      this.recipe?.tags?.push(this.tagAddSelect);
      this.tagAddSelect = null;
    },
    addNewTag(new_tag: string) {
      // , done: CallableFunction
      console.debug('Add new tag: ', new_tag);
      if (!new_tag) {
        return;
      }
      let exists = this.recipe?.tags?.find(
        (t) => t.title.toLowerCase() === new_tag.toLowerCase()
      );
      if (exists) {
        // If tag with this name already added to recipe
        console.debug('Tag already exists!');
        return;
      }

      let existsNotUsed = this.tags?.find(
        (t) => t.title.toLowerCase() === new_tag.toLowerCase()
      );
      if (existsNotUsed) {
        // If tag with this name exists in DB
        console.debug('Using existing tag in DB');
        this.tagAddSelect = existsNotUsed;
        this.addTag();
        return;
      }

      this.tagAddSelect = {
        // @ts-expect-error: Tag will be created
        id: null,
        title: new_tag,
      };
      // done(new_tag, 'add-unique');
      this.addTag();
    },
    filterTags(val: string, update: CallableFunction) {
      update(() => {
        let isUsed = (tag: RecipeTag) => {
          return this.recipe?.tags?.some((t) => t.id == tag.id);
        };

        const needle = val.toLowerCase();
        let tags = this.tags;

        this.tagList =
          tags?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)) ||
          [];
        // console.debug(needle, this.tagList, tags);
      });
    },
    addIngredient(new_val?: string) {
      if (new_val && this.ingAdd && this.ingAdd.select) {
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
      this.recipe?.ingredients?.push({
        // @ts-expect-error: Ingredient will be added
        ingredient: this.ingAdd.select,
        amount: this.ingAdd.amount,
        amount_type: this.ingAdd.amount_type as AmountTypeEnum,
        is_main: false,
      });
      this.ingAdd = Object.assign({}, this.ingAddDefault);
    },

    removeIngredient(row: RecipeIngredientRead) {
      if (!this.recipe) {
        return;
      }
      console.debug('Remove ingredient: ', row);
      this.$q
        .dialog({
          title: 'Подтверждение удаления ингредиента',
          message: `Вы уверены что хотите удалить ингредиент '${
            row?.ingredient?.title || 'Новый ингредиент'
          }' ?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          console.debug('Remove ingredient confirmed');
          if (!this.recipe) {
            return;
          }
          this.recipe.ingredients =
            this.recipe?.ingredients?.filter((t) => {
              return t != row;
            }) || [];
        });
    },

    filterIngredients(val: string, update: CallableFunction) {
      update(() => {
        // let isUsed = (ing) => {
        //   // console.debug(ing, this.recipe.ingredients);
        //   return this.recipe.ingredients.some((t) => t.ingredient.id == ing.id);
        // };
        const needle = val.toLowerCase();
        let ingredients = this.ingredients;

        this.ingList =
          ingredients?.filter(
            (v) => v.title.toLowerCase().indexOf(needle) > -1 // && !isUsed(v)
          ) || [];
        // console.debug(needle, this.tagList, tags);
      });
    },

    filterIngredientsAmountType(val: string, update: CallableFunction) {
      update(() => {
        const needle = val.toLowerCase();
        let amount_types = (this.amount_types?.types || null) as AmountTypesTypes | null;

        this.amountTypeList =
          amount_types?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1) || [];
        // console.debug(needle, this.tagList, tags);
      });
    },
    dateTimeFormat(raw: Date | string | null): string {
      if (!raw) {
        return '-';
      }
      return date.formatDate(raw, 'YYYY.MM.DD hh:mm');
    },
    dateFormat(raw: Date | string): string {
      return date.formatDate(raw, 'YYYY.MM.DD');
    },
  },

  computed: {
    recipe() {
      return this.store.recipe as (RecipeRead & PatchedRecipeRead) | null;
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
    dense() {
      // return this.$q.screen.lt.sm;
      return true;
    },
    pricesPart(): number {
      return (
        this.recipe?.ingredients?.map((i) => i.price_part).reduce((a, b) => a + b, 0) || 0
      );
    },
    pricesFull(): number {
      return (
        this.recipe?.ingredients?.map((i) => i.price_full).reduce((a, b) => a + b, 0) || 0
      );
    },
  },

  watch: {
    edit(val) {
      let column_actions = {
        name: 'actions',
        label: 'Действия',
        field: () => '',
        required: true,
        sortable: true,
        style: '',
      };

      if (val) {
        this.ingredientsColumns.push(column_actions);
      } else {
        this.ingredientsColumns = this.ingredientsColumns?.filter(
          (i) => i !== column_actions
        );
      }
    },
    tagAddSelect() {
      this.addTag();
    },
  },
});
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
