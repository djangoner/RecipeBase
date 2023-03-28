/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WeekPlanCondition } from './WeekPlanCondition';

export type PaginatedWeekPlanConditionList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<WeekPlanCondition>;
};
