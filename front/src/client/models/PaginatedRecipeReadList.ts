/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeRead } from './RecipeRead';

export type PaginatedRecipeReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipeRead>;
};
