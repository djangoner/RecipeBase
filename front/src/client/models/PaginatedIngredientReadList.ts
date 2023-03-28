/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IngredientRead } from './IngredientRead';

export type PaginatedIngredientReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<IngredientRead>;
};
