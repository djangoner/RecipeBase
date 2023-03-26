<template>
  <q-form
    @submit="$emit('submit', $event)"
    @reset="$emit('reset', $event)"
  >
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Время готовки
      </h6>
      <q-range
        v-model="filters.cooking_time"
        class="q-px-md"
        :min="5"
        :max="120"
        :step="5"
        label
      />
    </div>

    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Метки
      </h6>
      <tags-select
        v-model="filters.tags_include"
        :exclude="filters.tags_exclude"
        label="Включить"
      />
      <tags-select
        v-model="filters.tags_exclude"
        :exclude="filters.tags_include"
        label="Исключить"
      />
    </div>
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Ингредиенты
      </h6>
      <ingredients-select
        v-model="filters.ingredients_include"
        :exclude="filters.ingredients_exclude"
        label="Включить"
      />
      <ingredients-select
        v-model="filters.ingredients_exclude"
        :exclude="filters.ingredients_include"
        label="Исключить"
      />
    </div>
    <div class="q-my-sm">
      <h6 class="q-my-sm text-subtitle2 text-bold">
        Рейтинг
      </h6>
    </div>

    <div class="q-my-sm">
      <div
        v-for="user of usersRate"
        :key="user.id"
        class="q-my-sm"
      >
        <div>
          <div
            class="row justify-between q-col-gutter-x-sm q-col-gutter-y-sm"
          >
            <span>
              {{ userReadable(user) }}
            </span>
          </div>
        </div>

        <q-range
          :model-value="userRating(user)"
          class="q-px-md"
          :min="0"
          :max="5"
          label
          @update:model-value="userSetRating(user, $event)"
        />
      </div>
    </div>

    <div class="row justify-around">
      <q-btn
        type="reset"
        color="negative"
        size="sm"
        icon="close"
      >
        Сбросить
      </q-btn>
      <q-btn
        type="submit"
        color="primary"
        size="sm"
        icon="search"
      >
        Поиск
      </q-btn>
    </div>
  </q-form>
</template>

<script lang="ts">
import TagsSelect from './TagsSelect.vue'
import IngredientsSelect from './IngredientsSelect.vue'
import { User } from 'src/client';
import { RangeValue, RecipesFilters } from 'src/modules/Globals';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { useAuthStore } from 'src/stores/auth';
import { useBaseStore } from 'src/stores/base';
import { defineComponent, PropType } from 'vue';


export default defineComponent({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { IngredientsSelect, TagsSelect },
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: {
      type: Object as PropType<RecipesFilters>,
        required: true,
    },
  },
  emits: ["update:model-value", "submit", "reset"],
  data(){
    const store = useBaseStore()
    const storeAuth = useAuthStore()
    return {store, storeAuth, loading: false}
  },
  computed: {
    filters: {
      get(){
        return this.modelValue
      },
      set(val: RecipesFilters){
        this.$emit("update:model-value", val)
      }
    },
    users() {
      return this.storeAuth?.users;
    },
    usersRate() {
      const users = this.users;
      if (!users) {
        return users;
      }
      return users.filter((u) => {
        return u?.profile?.show_rate;
      });
    },
  },
  created(){
    if (!this.users) {
        this.loadUsers();
      }
  },
  methods: {
    loadUsers() {
      const payload = {
        page_size: 1000,
        can_rate: true,
      };
      this.storeAuth
        .loadUsers(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          this.loading = false;
          this.handleErrors(err, "Ошибка загрузки пользователей");
        });
    },
    userRating(user: User) {
      const exists = this.filters?.ratings[user.id];
      // console.debug('userRating: ', user, exists);

      if (exists) {
        return exists;
      } else {
        return { min: 0, max: 5 };
      }
    },
    userSetRating(user: User, rating: RangeValue) {
      // console.debug('setUserRating: ', user, rating);

      this.filters.ratings[user.id] = rating;
    },
    userReadable(user: User): string {
      if (user.first_name) {
        return user.first_name + " " + String(user.last_name);
      }
      return user.username;
    },
  }
})
</script>