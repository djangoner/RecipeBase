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
              :class="rating ? weekDayColor(rating) : 'bg-cyan'"
            >
              <div>
                {{ rating && rating > 0 ? rating : "-" }}
              </div>
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </q-tab-panel>
  </q-tab-panels>
</template>

<script lang="ts">
import { RecipePlanWeekRead, User } from "src/client";
import { WeekDaysShort } from "src/modules/WeekUtils";
import { useAuthStore } from "src/stores/auth";
import { defineComponent, PropType } from "vue";
import HandleErrorsMixin, {
  CustomAxiosError,
} from "../modules/HandleErrorsMixin";

let ratingColors: { [key: number]: string } = {
  5: "bg-positive",
  4: "bg-green-4",
  3: "bg-amber",
  2: "bg-orange",
  1: "bg-deep-orange-4",
};

interface TagsStats {
  [key: string]: number;
}

export default defineComponent({
  props: {
    plan: { required: true, type: Object as PropType<RecipePlanWeekRead> },
  },
  mixins: [HandleErrorsMixin],
  data() {
    const storeAuth = useAuthStore();
    const defaultTab = this.$q.localStorage.getItem("week_tab") || "stats";
    return {
      storeAuth,
      tab: defaultTab as string,
      WeekDaysShort: WeekDaysShort as { [key: number]: string },
      loading: false,
    };
  },
  created() {
    if (!this.users) {
      this.loadUsers();
    }
  },
  methods: {
    loadUsers() {
      let payload = {
        pageSize: 1000,
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
    getRating(day_idx: number, user: User): number | null {
      if (!this.plan) {
        return null;
      }
      let dayRecipes = this.plan?.plans.filter(
        (plan) => plan.day == day_idx && plan.recipe && !plan.recipe.is_archived
      );

      let ratings = dayRecipes.map((r) => {
        let items: Array<number> = [];
        if (r?.recipe?.ratings) {
          items = r?.recipe?.ratings.map((r) => {
            let rate =
              typeof r.user == "number"
                ? r.user == user.id
                : r.user.id == user.id;
            return rate ? r.rating : -1;
          });
        }
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
    weekDaysRatings(user: User) {
      // :set="(rating = getRating(day, user))"
      return Object.entries(WeekDaysShort).map(([k]) => {
        return this.getRating(parseInt(k), user);
      });
    },
    weekDayColor(rating: number): string {
      return ratingColors[rating] || "bg-cyan";
    },
  },
  computed: {
    users(): User[] | null {
      return this.storeAuth?.users;
    },
    usersRate(): User[] | null {
      let users = this.users;
      if (!users) {
        return users;
      }
      return users.filter((u) => {
        return u?.profile?.show_rate;
      });
    },
    getTagsStats(): { [id: string]: number } | null {
      let stats: TagsStats = {};
      if (!this.plan || !this.plan.plans) {
        return null;
      }
      this.plan?.plans?.forEach((p) => {
        if (!p.recipe.tags) return;
        p.recipe.tags.forEach((t) => {
          if (!Object.prototype.hasOwnProperty.call(stats, t.title)) {
            stats[t.title] = 0;
          }
          stats[t.title] += 1;
        });
      });
      return stats;
    },
  },
  watch: {
    tab(val: string) {
      this.$q.localStorage.set("week_tab", val);
    },
  },
});
</script>
