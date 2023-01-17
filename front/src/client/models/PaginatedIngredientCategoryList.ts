/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IngredientCategory } from './IngredientCategory';

export type PaginatedIngredientCategoryList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<IngredientCategory>;
};
