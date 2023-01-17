/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ShopShort } from './ShopShort';

export type ShopIngredientCategory = {
    readonly id: number;
    shop: ShopShort;
    num?: number | null;
    category: number;
};
