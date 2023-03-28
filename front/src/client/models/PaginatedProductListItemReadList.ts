/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItemRead } from './ProductListItemRead';

export type PaginatedProductListItemReadList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<ProductListItemRead>;
};
