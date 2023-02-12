/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';
import type { IngredientRead } from './IngredientRead';
import type { RecipeIngredientWithRecipeRead } from './RecipeIngredientWithRecipeRead';

/**
 * Adds nested create feature
 */
export type ProductListItemRead = {
    readonly id: number;
    ingredient: IngredientRead;
    readonly amount_type_str: string;
    week: number;
    readonly packs: number;
    readonly price_part: number;
    readonly price_full: number;
    ingredients: Array<RecipeIngredientWithRecipeRead>;
    day?: number | null;
    readonly is_auto: boolean;
    is_deleted?: boolean;
    is_completed?: boolean;
    title: string;
    amount?: number | null;
    readonly amounts: Record<string, any>;
    amount_type?: AmountTypeEnum | null;
    description?: string | null;
    priority?: number;
    readonly created: string;
    author?: number | null;
    assigned?: number | null;
};
