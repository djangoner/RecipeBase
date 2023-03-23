/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ComparisonModeEnum } from './ComparisonModeEnum';
import type { ConditionEnum } from './ConditionEnum';
import type { PlanFieldEnum } from './PlanFieldEnum';
import type { SelectorTypeEnum } from './SelectorTypeEnum';

export type WeekPlanCondition = {
    readonly id: number;
    active?: boolean;
    title?: string | null;
    condition?: ConditionEnum | null;
    plan_field?: PlanFieldEnum | null;
    comparison_mode?: ComparisonModeEnum | null;
    selector_type?: SelectorTypeEnum | null;
    selector_value?: string | null;
    manual_value?: string | null;
    parent?: number | null;
};
