<template>
  <q-markup-table flat>
    <tbody class="table-rating">
      <tr v-for="user of usersRate" :key="user.id">
        <td class="cell-icon">
          <q-icon :name="user.profile.icon || 'person'" size="md"></q-icon>
        </td>

        <td class="cell-name">
          {{ user?.first_name ? user.first_name + ' ' + user?.last_name : user.username }}
        </td>

        <td class="cell-rating">
          <q-rating
            :modelValue="userRating(user) + 1"
            :readonly="!edit"
            @update:modelValue="userSetRating(user, $event - 1)"
            :icon="['thumb_down', 'star']"
            :color-selected="['grey', 'green-5']"
            :max="6"
            size="2em"
            color="primary"
          />
        </td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script>
import { useBaseStore } from 'src/stores/base';
import { useAuthStore } from 'src/stores/auth';

let defaultRating = {};

export default {
  props: {
    modelValue: { required: true },
    edit: { required: true },
  },
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    return {
      store,
      storeAuth,
    };
  },
  mounted() {
    this.loadUsers();
  },
  methods: {
    loadUsers() {
      let payload = {
        page_size: 1000,
        can_rate: true,
      };
      this.storeAuth
        .loadUsers(payload)
        .then(() => {
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки пользователей');
        });
    },
    userRating(user) {
      let exists = this.modelValue?.ratings?.filter((r) => {
        return r.user.id == user.id || r.user == user.id;
      });
      // console.debug('userRating: ', user, exists);

      if (exists && exists.length > 0) {
        return exists[0]?.rating || 0;
      } else {
        return -1;
      }
    },
    userSetRating(user, rating) {
      let exists = this.modelValue?.ratings.filter((r) => {
        return r.user.id == user.id;
      });
      // console.debug('setUserRating: ', user, rating, exists);

      if (exists && exists.length > 0) {
        let mvalue = Object.assign({}, this.modelValue);
        mvalue.ratings = mvalue.ratings.map((r) => {
          if (r.user.id == user.id) {
            r.rating = rating;
          }
          return r;
        });
        this.$emit('update:modelValue', mvalue);
      } else {
        let mvalue = Object.assign({}, this.modelValue);
        mvalue.ratings.push(
          Object.assign({}, defaultRating, {
            recipe: this.modelValue.id,
            user: user,
            rating: rating,
          })
        );
        this.$emit('update:modelValue', mvalue);
      }
    },
  },
  computed: {
    users() {
      return this.storeAuth?.users?.results;
    },
    usersRate() {
      let users = this.users;
      if (!users) {
        return users;
      }
      return users.filter((u) => {
        return u?.profile?.show_rate;
      });
    },
  },
};
</script>
