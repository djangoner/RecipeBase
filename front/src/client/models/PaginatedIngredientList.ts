/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Ingredient } from './Ingredient';

export type PaginatedIngredientList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<Ingredient>;
};
