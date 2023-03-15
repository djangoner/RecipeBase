/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';
import type { Ingredient } from './Ingredient';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
 */
export type RecipeIngredientRead = {
    readonly id: number;
    ingredient: Ingredient;
    readonly amount_type_str: string;
    readonly packs: number;
    readonly price_part: number;
    readonly price_full: number;
    amount: number;
    readonly amount_grams: number | null;
    amount_type?: AmountTypeEnum;
    is_main?: boolean;
    recipe?: number;
};
