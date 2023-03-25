<template>
  <q-tree
    v-model:selected="selected"
    :nodes="warningsNodes"
    selected-color="primary"
    node-key="id"
    dense
    default-expand-all
  />
  <!-- <q-list dense>
    <q-item v-for="(warnings, cond) of warningsGrouped" :key="cond">
      <q-item-section>
        {{ conditionName(getCondition(cond)) }} ({{ warnings.length }})
      </q-item-section>
    </q-item>
  </q-list> -->
</template>

<script lang="ts">
import { date, QTreeNode } from "quasar";
import { ConditionWarning, WeekPlanCondition } from "src/client";
import { getWarningPriorityColor } from "src/modules/Utils";
import { getDateOfISOWeek, YearWeek } from "src/modules/WeekUtils";
import { useBaseStore } from "src/stores/base";
import { defineComponent, PropType } from "vue";

interface warningsGrouped {
  [key: number]: ConditionWarning[];
}
type StrToStr = { [key: string]: string };

const ComparisonModes: StrToStr = {
  eq: "=",
  neq: "!=",
  gt: ">",
  ge: ">=",
  lt: "<",
  le: "<=",
};

const StrConditions: StrToStr = {
  and: "и",
  or: "или",
  not: "не",
};

export default defineComponent({
  props: {
    warnings: { type: Array as PropType<ConditionWarning[]>, required: true },
    week: { required: true, type: Object as PropType<YearWeek> },
  },
  data() {
    const store = useBaseStore();
    return {
      store,
      loading: false,
      selected: null as ConditionWarning | null,
      groupByField: "condition" as "condition" | "plan",
    };
  },
  computed: {
    conditions() {
      return this.store.conditions;
    },
    plans() {
      return this.store.week_plan?.plans || [];
    },
    warningsGrouped(): warningsGrouped {
      const res: warningsGrouped = {};
      for (const cond of this.warnings) {
        const idVal = cond[this.groupByField];
        if (!Object.hasOwn(res, idVal)) {
          res[idVal] = [];
        }
        res[idVal].push(cond);
      }
      return res;
    },
    warningsNodes() {
      const res: QTreeNode[] = [];
      for (const [condID, warnings] of Object.entries(this.warningsGrouped)) {
        const r = this.warningNodeRender(
          {
            condition: Number(condID),
            value_current: "",
            value_expected: "",
            plan: 0,
            childrens: [],
          },
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
          warnings
        );
        if (!r) {
          continue;
        }
        res.push(r);
      }
      return res;
    },
    warnedPlans(): number[] {
      const plans = this.warnings.map((w) => w.plan);
      return [...new Set(plans)];
    },
  },
  methods: {
    conditionName(cond: WeekPlanCondition | null): string {
      if (!cond) {
        return "";
      }
      return cond?.title ? `#${cond.id}.${cond.title}` : `#${cond?.id}`;
    },
    subconditionName(cond: WeekPlanCondition | null): string {
      if (!cond) {
        return "";
      }
      if (cond.title) {
        return cond.title;
      }
      return "?";
    },
    getCondition(id: number) {
      return this.conditions?.find((c) => c.id == id) || null;
    },
    getPlan(id: number) {
      return this.plans?.find((c) => c.id == id) || null;
    },
    getDay(idx: number): string {
      const fday = getDateOfISOWeek(this.week.year, this.week.week);
      fday.setDate(fday.getDate() + idx);
      return date.formatDate(fday, "DD.MM");
    },
    conditionAsString(warn: ConditionWarning) {
      const cond = this.getCondition(warn.condition);
      let sign = String(cond?.comparison_mode) || "";

      if (sign) {
        sign = ComparisonModes[sign] || sign;
      }
      const val1 = warn.value_current;
      const val2 = warn.value_expected;

      return `${val1} ${sign} ${val2}`;
    },
    warningNodeRender(
      rootCond: ConditionWarning,
      warnings: ConditionWarning[]
    ): QTreeNode | null {
      const cond = this.getCondition(Number(rootCond.condition));
      if (!cond) {
        return null;
      }

      let label = this.conditionName(cond);
      if (rootCond.plan) {
        const plan = this.getPlan(rootCond.plan);
        if (plan && plan.day) {
          const dayStr = this.getDay(plan.day - 1);
          const failTx = this.conditionAsString(rootCond);
          if (cond.condition) {
            const condStr =
              StrConditions[cond.condition].toUpperCase() || cond.condition;

            label = `${dayStr || ""} ${
              plan.meal_time.title
            } (условие ${condStr})`;
          } else {
            label = `${dayStr || ""} ${plan.meal_time.title} ${failTx} (${
              cond.plan_field || ""
            })`;
          }
        }
      }
      const r: QTreeNode = {
        label: label,
        id: String(cond.id) + "_" + label,
        icon: "warning",
        iconColor: getWarningPriorityColor(String(cond.priority)),
        children: [] as QTreeNode[],
      };
      if (cond.icon) {
        r.icon = String(cond.icon);
      }
      warnings.forEach((w) => {
        // console.debug("Children: ", w);

        const subNode = this.warningNodeRender(w, w.childrens);
        if (subNode && r.children) {
          r.children.push(subNode);
        }
      });
      // console.debug("Res:", r);
      return r;
    },
  },
});
</script>
