/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IngredientCategory } from './IngredientCategory';

/**
 * Adds nested create feature
 */
export type IngredientRead = {
    readonly id: number;
    readonly used_times: number;
    category: IngredientCategory;
    title: string;
    description?: string | null;
    /**
     * Минимальный размер упаковки в граммах / миллилитрах
     */
    min_pack_size?: number | null;
    item_weight?: number | null;
    price?: number | null;
    need_buy?: boolean;
    edible?: boolean;
};
