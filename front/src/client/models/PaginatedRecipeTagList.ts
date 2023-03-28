/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeTag } from './RecipeTag';

export type PaginatedRecipeTagList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipeTag>;
};
