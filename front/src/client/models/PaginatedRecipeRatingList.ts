/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeRating } from './RecipeRating';

export type PaginatedRecipeRatingList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipeRating>;
};
