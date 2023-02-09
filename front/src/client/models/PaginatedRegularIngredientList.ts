/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RegularIngredient } from './RegularIngredient';

export type PaginatedRegularIngredientList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<RegularIngredient>;
};
