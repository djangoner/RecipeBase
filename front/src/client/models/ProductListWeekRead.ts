/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProductListItemRead } from './ProductListItemRead';

/**
 * Adds nested create feature
 */
export type ProductListWeekRead = {
    readonly id: number;
    items: Array<ProductListItemRead>;
    year: number;
    week: number;
};
