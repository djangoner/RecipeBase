<template>
  <div class="q-my-md">
    <div class="roq q-gutter-y-md">
      <draggable
        class="row column no-wrap q-gutter-md q-mx-auto"
        v-model="images"
        v-if="images"
        group="recipeImages"
        handle=".handle"
        @start="drag = true"
        @end="drag = false"
        @change="onOrderChange"
        item-key="num"
      >
        <template #item="{ element }">
          <div class="row items-center q-gutter-x-sm">
            <q-icon class="handle" name="drag_indicator" size="md"></q-icon>
            <q-icon
              class="cursor-pointer"
              name="delete"
              size="sm"
              color="negative"
              @click="askDelete(element)"
            ></q-icon>

            <span> {{ String(element.num || "0").padStart(2, "0") }} : </span>
            <q-input v-model="element.title" label="Название файла"> </q-input>
            <!-- Image content -->
            <div style="flex: 1 1 50px">
              <q-img
                :src="element.upload_preview || element.image"
                height="100px"
                fit="contain"
              ></q-img>
            </div>
          </div>
        </template>
      </draggable>
    </div>
    <!-- <div class="row no-wrap items-center" v-for="img of modelValue" :key="img.id">
      <q-icon name="drag_indicator" size="md"></q-icon>
      <q-img :src="img.image" height="100px" fit="contain"></q-img>
    </div> -->

    <div class="q-mt-md">
      <q-file
        v-model="upload_file"
        ref="upload_field"
        class="my-md"
        v-show="0"
        style="width: 200px; margin-left: auto; margin-right: auto"
        label="Загрузка файла"
        filled
      ></q-file>
      <q-btn
        icon="add"
        label="Загрузить изображение"
        size="sm"
        @click="openFileSelect()"
      ></q-btn>
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
  data() {
    return {
      upload_file: null as File | null,
      drag: false,
      images: [] as RecipeImage[],
    };
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

  watch: {
    images(newVal, oldVal) {
      console.debug("Updated recipe from imagesUpload!", newVal, oldVal);
      // if (newVal != oldVal) {
      //   return;
      // }
      this.$emit("update:modelValue", newVal);
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
});
</script>
