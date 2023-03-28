/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ShopIngredientCategory } from './ShopIngredientCategory';

export type IngredientCategory = {
    readonly id: number;
    sorting: Array<ShopIngredientCategory>;
    title: string;
    icon?: string | null;
};
