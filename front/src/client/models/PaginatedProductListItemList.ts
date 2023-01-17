/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItem } from './ProductListItem';

export type PaginatedProductListItemList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<ProductListItem>;
};
