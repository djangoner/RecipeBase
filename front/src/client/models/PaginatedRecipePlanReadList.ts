/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipePlanRead } from './RecipePlanRead';

export type PaginatedRecipePlanReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipePlanRead>;
};
