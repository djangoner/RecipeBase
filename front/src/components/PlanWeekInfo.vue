<template>
  <q-tabs v-model="tab" dense>
    <q-tab name="stats" icon="info" />
    <q-tab name="eats" icon="people" />
  </q-tabs>

  <q-tab-panels v-model="tab" animated>
    <q-tab-panel name="stats">
      <div class="text-center text-subtitle1 q-mb-sm">Метки</div>
      <q-markup-table flat dense>
        <tbody>
          <tr v-for="(stat, tag) in getTagsStats" :key="tag">
            <td class="text-left">{{ tag }}</td>
            <td class="text-center">{{ stat }}</td>
            <td class="text-center">-</td>
          </tr>
        </tbody>
      </q-markup-table>
    </q-tab-panel>
    <q-tab-panel name="eats" class="q-px-sm">
      <q-markup-table flat dense>
        <thead>
          <tr>
            <th>#</th>
            <th v-for="(day, idx) in WeekDaysShort" :key="idx">{{ day }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user of usersRate" :key="user.id">
            <td style="width: 50px">{{ user?.first_name || user.username }}</td>

            <td
              v-for="(rating, idx) in weekDaysRatings(user)"
              :key="idx"
              class="text-center"
              :class="weekDayColor(rating)"
            >
              <div>
                {{ rating > 0 ? rating : '-' }}
              </div>
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </q-tab-panel>
  </q-tab-panels>
</template>

<script>
import { WeekDaysShort } from 'components/WeekSelect.vue';
import { useAuthStore } from 'src/stores/auth';

let ratingColors = {
  5: 'bg-positive',
  4: 'bg-green-4',
  3: 'bg-amber',
  2: 'bg-orange',
  1: 'bg-deep-orange-4',
};

export default {
  props: {
    plan: { required: true },
  },
  data() {
    const storeAuth = new useAuthStore();
    return {
      storeAuth,
      tab: this.$q.localStorage.getItem('week_tab') || 'stats',
      WeekDaysShort,
    };
  },
  mounted() {
    if (!this.users) {
      this.loadUsers();
    }
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
    getRating(day_idx, user) {
      if (!this.plan) {
        return '-';
      }
      let dayRecipes = this.plan?.plans.filter((plan) => plan.day == day_idx);

      let ratings = dayRecipes.map((r) => {
        let items = r?.recipe?.ratings.map((r) => {
          let rate = r.user.id == user.id || r.user == user.id;
          return rate ? r.rating : -1;
        });
        if (!items) {
          return -1;
        }
        return Math.max(...items);
      });

      let rate = ratings.length > 0 ? Math.max(...ratings) : -1;

      // if (dayRecipes) {
      //   console.debug(day_idx, user.username, dayRecipes, ratings);
      // }
      return rate;
    },
    weekDaysRatings(user) {
      // :set="(rating = getRating(day, user))"
      return Object.entries(WeekDaysShort).map(([k, v]) => {
        return this.getRating(k, user);
      });
    },
    weekDayColor(rating) {
      return ratingColors[rating] || 'bg-cyan';
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
    getTagsStats() {
      let stats = {};
      this.plan?.plans?.forEach((p) => {
        p.recipe.tags.forEach((t) => {
          if (!stats.hasOwnProperty(t.title)) {
            stats[t.title] = 0;
          }
          stats[t.title] += 1;
        });
      });
      return stats;
    },
  },
  watch: {
    tab(val) {
      this.$q.localStorage.set('week_tab', this.tab);
    },
  },
};
</script>
