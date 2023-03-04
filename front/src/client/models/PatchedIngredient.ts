/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RegularIngredient } from './RegularIngredient';

/**
 * Adds nested create feature
 */
export type PatchedIngredient = {
    readonly id?: number;
    readonly used_times?: number;
    category?: number | null;
    readonly regular_ingredients?: RegularIngredient;
    image?: string | null;
    title?: string;
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
