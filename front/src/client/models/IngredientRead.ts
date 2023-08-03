/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RegularIngredient } from './RegularIngredient';
import type { TypeE5eEnum } from './TypeE5eEnum';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
 */
export type IngredientRead = {
    readonly id: number;
    readonly used_times: number;
    category?: number | null;
    readonly regular_ingredients: RegularIngredient;
    image?: string | null;
    readonly image_thumbnail: string;
    readonly image_thumbnail_webp: string;
    title: string;
    description?: string | null;
    /**
     * Минимальный размер упаковки в граммах / миллилитрах
     */
    min_pack_size?: number | null;
    item_weight?: number | null;
    type?: TypeE5eEnum | null;
    price?: number | null;
    need_buy?: boolean;
    edible?: boolean;
    /**
     * Сколько дней продукт хранится свежим
     */
    fresh_days?: number | null;
};
