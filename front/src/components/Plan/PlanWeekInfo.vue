<template>
  <q-tabs
    v-model="tab"
    dense
  >
    <q-tab
      name="info"
      icon="info"
      class="text-info"
    >
      <q-badge
        v-if="weekCommentFilled"
        color="teal"
        floating
      >
        <q-icon name="comment" />
      </q-badge>
    </q-tab>
    <q-tab
      name="warnings"
      icon="warning"
      class="text-orange"
    >
      <q-badge
        v-if="warningsCount"
        color="red"
        floating
      >
        {{
          warningsCount
        }}
      </q-badge>
    </q-tab>
    <q-tab
      name="eats"
      icon="people"
    />
  </q-tabs>

  <q-tab-panels
    v-model="tab"
    style="height: 230px"
    animated
  >
    <q-tab-panel
      name="info"
      class=" q-pb-xs"
    >
      <plan-tab-info
        :readonly="readonly"
        @update-plan="$emit('update-plan', $event)"
      />
    </q-tab-panel>
    <q-tab-panel name="warnings">
      <template v-if="!store.condWarnings || !store.condWarnings.length">
        <div class="text-subtitle1 flex flex-center full-height">
          Нет предупреждений
        </div>
      </template>
      <condition-warnings
        v-else-if="conditions"
        :warnings="store.condWarnings"
        :week="week"
      />
      <q-inner-loading :showing="!conditions" />
    </q-tab-panel>
    <q-tab-panel
      name="eats"
      class="q-px-sm"
    >
      <q-markup-table
        flat
        dense
      >
        <thead>
          <tr>
            <th>#</th>
            <th
              v-for="(day, idx) in WeekDaysShort"
              :key="idx"
            >
              {{ day }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user of usersRate"
            :key="user.id"
          >
            <td style="width: 50px">
              {{ user?.first_name || user.username }}
            </td>

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
import PlanTabInfo from './PlanTabInfo.vue'
import { RecipePlanWeekRead, User } from "src/client";
import { WeekDaysShort, YearWeek } from "src/modules/WeekUtils";
import { useAuthStore } from "src/stores/auth";
import { useBaseStore } from "src/stores/base";
import { defineComponent, PropType } from "vue";
import ConditionWarnings from "./ConditionWarnings.vue";
import { useShortcutcs } from 'src/modules/VueUtils';

const ratingColors: { [key: number]: string } = {
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
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  components: { ConditionWarnings, PlanTabInfo },
  props: {
    plan: { required: true, type: Object as PropType<RecipePlanWeekRead> },
    week: { required: true, type: Object as PropType<YearWeek> },
    readonly: {type: Boolean, default: false},
  },
  emits: ["update-plan"],
  data() {
    const store = useBaseStore();
    const storeAuth = useAuthStore();
    const defaultTab = this.$q.localStorage.getItem("week_tab") || "warnings";
    return {
      store,
      storeAuth,
      tab: defaultTab as string,
      WeekDaysShort: WeekDaysShort as { [key: number]: string },
      loading: false,
    };
  },
  computed: {
    users(): User[] | null {
      return this.storeAuth?.users;
    },
    usersRate(): User[] | null {
      const users = this.users;
      if (!users) {
        return users;
      }
      return users.filter((u) => {
        return u?.profile?.show_rate;
      });
    },
    getTagsStats(): { [id: string]: number } | null {
      const stats: TagsStats = {};
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
    conditions() {
      return this.store.conditions;
    },
    warningsCount(): number {
      if (!this.plan || !this.store.condWarnings) {
        return 0;
      }
      return this.store.condWarnings.length;
    },
    weekCommentFilled(){
      return Boolean(this.plan?.comments["week"]) || false
    }
  },
  watch: {
    tab(val: string) {
      this.$q.localStorage.set("week_tab", val);
    },
  },
  mounted(){
    useShortcutcs({
      alt_1: () => this.tab = "info",
      alt_2: () => this.tab = "warnings",
      alt_3: () => this.tab = "eats",
    })
  },
  created() {
    if (!this.users) {
      this.loadUsers();
    }
    this.loadConditions();
  },
  methods: {
    loadUsers() {
      const payload = {
        pageSize: 1000,
        can_rate: true,
      };
      this.storeAuth
        .loadUsers(payload)
        .finally(() => {
          this.loading = false;
        })
    },
    getRating(day_idx: number, user: User): number | null {
      if (!this.plan) {
        return null;
      }
      const dayRecipes = this.plan?.plans.filter(
        (plan) => plan.day == day_idx && plan.recipe && !plan.recipe.is_archived
      );

      const ratings = dayRecipes.map((r) => {
        let items: Array<number> = [];
        if (r?.recipe?.ratings) {
          items = r?.recipe?.ratings.map((r) => {
            const rate =
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

      const rate = ratings.length > 0 ? Math.max(...ratings) : -1;

      // if (dayRecipes) {
      //   console.debug(day_idx, user.username, dayRecipes, ratings);
      // }
      return rate;
    },
    loadConditions() {
      const payload = { pageSize: 1000 };
      void this.store.loadConditions(payload)
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
});
</script>
