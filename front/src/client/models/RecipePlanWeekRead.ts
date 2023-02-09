/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlanRead } from './RecipePlanRead';

/**
 * Adds nested create feature
 */
export type RecipePlanWeekRead = {
    readonly id: number;
    plans: Array<RecipePlanRead>;
    year: number;
    week: number;
    comments?: Record<string, any>;
};
