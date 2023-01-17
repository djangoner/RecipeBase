/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlan } from './RecipePlan';

/**
 * Adds nested create feature
 */
export type PatchedRecipePlanWeek = {
    readonly id?: number;
    plans?: Array<RecipePlan>;
    year?: number;
    week?: number;
    comments?: Record<string, any>;
};
