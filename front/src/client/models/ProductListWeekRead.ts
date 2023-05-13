/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItemRead } from './ProductListItemRead';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
 */
export type ProductListWeekRead = {
    readonly id: number;
    items: Array<ProductListItemRead>;
    year: number;
    week: number;
    is_filled?: boolean;
};
