/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListWeekRead } from './ProductListWeekRead';

export type PaginatedProductListWeekReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<ProductListWeekRead>;
};
