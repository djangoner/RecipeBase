/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Recipe } from './Recipe';

export type PaginatedRecipeList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<Recipe>;
};
