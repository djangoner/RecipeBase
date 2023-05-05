<template>
  <q-markup-table flat>
    <tbody class="table-rating">
      <tr
        v-for="user of usersRate"
        :key="user.id"
      >
        <td class="cell-icon">
          <q-icon
            :name="user.profile.icon || 'person'"
            size="md"
          />
        </td>

        <td class="cell-name">
          {{
            user?.first_name
              ? user.first_name + " " + user?.last_name
              : user.username
          }}
        </td>


        <td class="cell-rating">
          <q-rating
            :model-value="userRating(user) + 1"
            :readonly="!edit"
            :icon="['thumb_down', 'star']"
            :color-selected="['grey', 'green-5']"
            :max="6"
            size="2em"
            :color="$q.dark.isActive ? 'grey-4' : 'primary'"
            @update:model-value="userSetRating(user, $event - 1)"
          />
          <q-tooltip>
            Текущая оценка: {{ userRating(user) || "-" }}
          </q-tooltip>
        </td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script lang="ts">
import { useBaseStore } from "src/stores/base";
import { useAuthStore } from "src/stores/auth";
import { defineComponent, PropType } from "vue";
import { RecipeRead, User } from "src/client";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "src/modules/HandleErrorsMixin";

const defaultRating = {};

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    modelValue: { required: true, type: Object as PropType<RecipeRead> },
    edit: { required: true, type: Boolean },
  },
  emits: ['update:model-value'],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    return {
      store,
      storeAuth,
      loading: false,
    };
  },
  computed: {
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
  created() {
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
      const exists = this.modelValue?.ratings?.filter((r) => {
        return typeof r.user == "number"
          ? r.user == user.id
          : r.user.id == user.id;
      });
      // console.debug('userRating: ', user, exists);

      if (exists && exists.length > 0) {
        const rating = exists[0]?.rating
        return rating !== null ? rating : -2;
      } else {
        return -1;
      }
    },
    userSetRating(user: User, rating: number | null) {
      if (!this.modelValue || !this.modelValue?.ratings) {
        return;
      }
      if (rating == -1){
        rating = null
      }

      const exists =
        this.modelValue?.ratings.filter((r) => {
          return r.user.id == user.id;
        }) || false;
      // console.debug('setUserRating: ', user, rating, exists);

      if (exists && exists.length > 0 && this.modelValue.ratings) {
        const mvalue = Object.assign({}, this.modelValue);
        mvalue.ratings = this.modelValue.ratings.map((r) => {
          if (r.user.id == user.id) {
            r.rating = rating;
          }
          return r;
        });
        this.$emit("update:model-value", mvalue);
      } else {
        const mvalue = Object.assign({}, this.modelValue);
        // @ts-expect-error: Rating will be created
        mvalue.ratings.push(
          // @ts-expect-error: Rating will be created
          Object.assign({}, defaultRating, {
            recipe: this.modelValue.id,
            user: user,
            rating: rating,
          })
        );
        this.$emit("update:model-value", mvalue);
      }
    },
  },
});
</script>
