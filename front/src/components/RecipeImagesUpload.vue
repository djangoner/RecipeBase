<template>
  <div class="q-my-md">
    <div class="roq q-gutter-y-md">
      <draggable
        v-if="images"
        v-model="images"
        class="row column no-wrap q-gutter-md q-mx-auto"
        group="recipeImages"
        handle=".handle"
        item-key="num"
        @start="drag = true"
        @end="drag = false"
        @change="onOrderChange"
      >
        <template #item="{ element }">
          <div class="row items-center q-gutter-x-sm">
            <q-icon
              class="handle"
              name="drag_indicator"
              size="md"
            />
            <q-icon
              class="cursor-pointer"
              name="delete"
              size="sm"
              color="negative"
              @click="askDelete(element)"
            />

            <span> {{ String(element.num || "0").padStart(2, "0") }} : </span>
            <q-input
              v-model="element.title"
              label="Название файла"
            />
            <!-- Image content -->
            <div style="flex: 1 1 50px">
              <q-img
                :src="element.upload_preview || element.image"
                height="100px"
                fit="contain"
              />
            </div>
          </div>
        </template>
      </draggable>
    </div>

    <div class="q-mt-md">
      <q-file
        v-show="0"
        ref="upload_field"
        v-model="upload_file"
        class="my-md"
        style="width: 200px; margin-left: auto; margin-right: auto"
        label="Загрузка файла"
        filled
      />
      <q-btn
        icon="add"
        label="Загрузить изображение"
        size="sm"
        @click="openFileSelect()"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { RecipeImage } from "src/client";
import { defineComponent, PropType } from "vue";
import draggable from "vuedraggable";

interface FileInput extends HTMLInputElement {
  pickFiles: CallableFunction;
}

export default defineComponent({
  components: {
    draggable,
  },
  props: {
    modelValue: { required: true, type: Array as PropType<RecipeImage[]> },
  },
  emits: ['update:model-value'],
  data() {
    return {
      upload_file: null as File | null,
      drag: false,
      images: [] as RecipeImage[],
    };
  },

  watch: {
    images(newVal, oldVal) {
      console.debug("Updated recipe from imagesUpload!", newVal, oldVal);
      // if (newVal != oldVal) {
      //   return;
      // }
      this.$emit("update:model-value", newVal);
    },
    modelValue(newVal: RecipeImage[], oldVal) {
      console.debug("Updated imagesUpload from recipe!", newVal, oldVal);
      if (newVal != oldVal) {
        return;
      }
      this.images = newVal;
      this.onOrderChange();
    },
    upload_file(val: File) {
      if (!val) {
        return;
      }
      this.images.push({
        id: this.images.length + 1,
        // @ts-expect-error: file will be converted on sending
        image: val,
        upload_preview: URL.createObjectURL(val),
        title: val.name,
      });
      this.onOrderChange();
      // console.debug(val);
      this.upload_file = null;
    },
  },
  created() {
    this.images = this.modelValue;
  },
  methods: {
    openFileSelect() {
      // console.debug('Add img: ', this.$refs.upload_field);
      const uploadField = this.$refs.upload_field as FileInput;
      uploadField.pickFiles();
    },
    onOrderChange() {
      this.images = this.images.map((p, idx) => {
        return { ...p, num: idx + 1 };
      });
    },
    deleteImg(img: RecipeImage) {
      this.images = this.images.filter((t) => {
        return t.num != img.num;
      });
    },
    askDelete(elem: RecipeImage) {
      console.debug("askDelete: ", elem);
      this.$q
        .dialog({
          title: "Подтверждение",
          message: `Вы уверены что хотите удалить изображение '${
            elem.title || "Новое изображение"
          }' ?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.deleteImg(elem);
          this.onOrderChange();
        });
    },
  },
});
</script>
