/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlanShort } from './RecipePlanShort';

/**
 * Adds nested create feature
 */
export type RecipePlanWeek = {
    readonly id: number;
    plans: Array<RecipePlanShort>;
    year: number;
    week: number;
    comments?: Record<string, any>;
};
