<template>
  <q-chip
    v-for="tag of recipeTags"
    :key="tag.id"
    class="cursor-pointer"
    :removable="edit"
    @remove="removeTag(tag)"
  >
    {{ tag.title }}
  </q-chip>
  <q-select
    v-if="edit && tags"
    v-model="tagAddSelect"
    label="Добавить метку"
    keydown.enter.prevent="addTag()"
    :input-debounce="0"
    :options="tags"
    :options-dense="dense"
    :dense="dense"
    option-label="title"
    use-input
    new-value-mode="add-unique"
    @filter="filterTags"
    @new-value="addNewTag"
  >
    <template #no-option>
      <q-item>
        <q-item-section class="text-grey">
          Нет результатов
        </q-item-section>
      </q-item>
    </template>
    <template #after>
      <q-btn
        icon="add"
        size="sm"
        color="positive"
        @click="addTag()"
      />
    </template>
  </q-select>
</template>
<script lang="ts">
import { RecipeTag } from "src/client"
import HandleErrorsMixin, { CustomAxiosError } from "src/modules/HandleErrorsMixin"
import { useBaseStore } from "src/stores/base"
import { defineComponent, PropType } from "vue"

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    edit: {
      type: Boolean,
      default: false,
    },
    recipeTags: {
      type: Array as PropType<RecipeTag[]>,
      default: () => [],
      required: false,
    },
  },
  emits: ['update:recipe-tags'],
  data() {
    const store = useBaseStore()
    return { store, search: "", tagAddSelect: null as RecipeTag | null }
  },
  computed: {
    tags() {
      const isUsed = (tag: RecipeTag) => {
        return this.recipeTags?.some((t) => t.id == tag.id)
      }

      const needle = this.search.toLowerCase()
      const tags = this.store.tags
      return tags?.filter((v) => v.title.toLowerCase().indexOf(needle) > -1 && !isUsed(v)) || []
      // console.debug(needle, this.tagList, tags);
    },
    dense(){
      return true;
    }
  },
  watch: {
    tagAddSelect() {
      this.addTag()
    },
  },
  created() {
    if (!this.store.tags) {
      this.loadTags()
    }
  },
  methods: {
    loadTags() {
      const payload = {
        pageSize: 1000,
      }
      this.store
        .loadTags(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, "Ошибка загрузки меток")
        })
    },
    filterTags(val: string, update: CallableFunction) {
      update(() => {
        this.search = val.toLowerCase()
      })
    },
    updateRootTags(tags: RecipeTag[]) {
      const newTags = tags
      console.debug("Update tags: ", newTags)
      this.$emit("update:recipe-tags", newTags)
    },
    addTag() {
      console.debug("Add tag: ", this.tagAddSelect)
      if (!this.tagAddSelect) {
        return
      }

      this.updateRootTags([].concat(this.recipeTags, this.tagAddSelect))
      this.tagAddSelect = null
    },
    addNewTag(new_tag: string) {
      // , done: CallableFunction
      console.debug("Add new tag: ", new_tag)
      if (!new_tag) {
        return
      }
      const exists = this.recipeTags?.find((t) => t.title.toLowerCase() === new_tag.toLowerCase())
      if (exists) {
        // If tag with this name already added to recipe
        console.debug("Tag already exists!")
        return
      }

      const existsNotUsed = this.tags?.find((t) => t.title.toLowerCase() === new_tag.toLowerCase())
      if (existsNotUsed) {
        // If tag with this name exists in DB
        console.debug("Using existing tag in DB")
        this.tagAddSelect = existsNotUsed
        this.addTag()
        return
      }

      this.tagAddSelect = {
        // @ts-expect-error: Tag will be created
        id: null,
        title: new_tag,
      }
      // done(new_tag, 'add-unique');
      this.addTag()
    },
    removeTag(tag: RecipeTag) {
      console.debug("Remove tag: ", tag)
      this.updateRootTags(this.recipeTags?.filter((t) => {
          return t.title !== tag.title
        }) || [])
    },
  },
})
</script>
