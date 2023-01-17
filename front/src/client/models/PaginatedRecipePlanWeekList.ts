/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlanWeek } from './RecipePlanWeek';

export type PaginatedRecipePlanWeekList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipePlanWeek>;
};
