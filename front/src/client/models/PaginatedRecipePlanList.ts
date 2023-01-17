/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlan } from './RecipePlan';

export type PaginatedRecipePlanList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipePlan>;
};
