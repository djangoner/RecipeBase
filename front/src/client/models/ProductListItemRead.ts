/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';
import type { IngredientRead } from './IngredientRead';
import type { RecipeIngredientWithRecipeRead } from './RecipeIngredientWithRecipeRead';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
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
    already_completed?: boolean;
    amount_completed?: number | null;
    title: string;
    amount?: number | null;
    readonly amounts: Record<string, any>;
    amount_type?: AmountTypeEnum | null;
    description?: string | null;
    priority?: number;
    readonly created: string;
    /**
     * Номер дня на который отложить покупку
     */
    buy_later?: string | null;
    author?: number | null;
    assigned?: number | null;
};
