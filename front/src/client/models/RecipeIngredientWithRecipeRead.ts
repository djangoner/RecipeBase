/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';
import type { RecipeShort } from './RecipeShort';

/**
 * Adds nested create feature
 */
export type RecipeIngredientWithRecipeRead = {
    readonly id: number;
    ingredient: number;
    readonly amount_type_str: string;
    readonly packs: number;
    readonly price_part: number;
    readonly price_full: number;
    recipe: RecipeShort;
    amount: number;
    readonly amount_grams: number | null;
    amount_type?: AmountTypeEnum;
    is_main?: boolean;
};
