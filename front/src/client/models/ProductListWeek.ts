/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItem } from './ProductListItem';

/**
 * Adds nested create feature
 */
export type ProductListWeek = {
    readonly id: number;
    items: Array<ProductListItem>;
    year: number;
    week: number;
};
