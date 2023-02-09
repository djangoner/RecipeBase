/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeImage } from './RecipeImage';

export type PaginatedRecipeImageList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RecipeImage>;
};
