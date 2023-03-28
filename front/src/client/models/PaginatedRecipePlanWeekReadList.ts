/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlanWeekRead } from './RecipePlanWeekRead';

export type PaginatedRecipePlanWeekReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipePlanWeekRead>;
};
