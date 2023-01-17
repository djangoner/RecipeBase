/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListWeek } from './ProductListWeek';

export type PaginatedProductListWeekList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<ProductListWeek>;
};
