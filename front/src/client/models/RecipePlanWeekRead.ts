/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ConditionWarning } from './ConditionWarning';
import type { RecipePlanRead } from './RecipePlanRead';

export type RecipePlanWeekRead = {
    readonly id: number;
    plans: Array<RecipePlanRead>;
    readonly warnings: Array<ConditionWarning>;
    readonly edited_first: string;
    readonly edited_last: string;
    year: number;
    week: number;
    comments?: Record<string, any>;
    is_filled?: boolean;
};
