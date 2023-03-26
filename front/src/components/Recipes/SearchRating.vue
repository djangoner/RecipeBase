<template>
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
</template>

<script lang="ts">
import { User } from 'src/client';
import { RangeValue, RecipesFilters } from 'src/modules/Globals';
import { useAuthStore } from 'src/stores/auth';
import { useBaseStore } from 'src/stores/base';
import { defineComponent, PropType } from 'vue';

export default defineComponent({
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
        .finally(() => {
          this.loading = false;
        })
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
  },
})
</script>