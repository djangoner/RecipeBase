/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItem } from './ProductListItem';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
 */
export type ProductListWeek = {
    readonly id: number;
    items?: Array<ProductListItem>;
    year: number;
    week: number;
    is_filled?: boolean;
    is_actual?: boolean;
};
