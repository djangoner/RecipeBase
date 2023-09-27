/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';
import type { RecipeShort } from './RecipeShort';

export type RecipeIngredientRecommendation = {
    readonly id: number;
    ingredient?: number | null;
    readonly amount_type_str: string;
    recipe: RecipeShort;
    amount: number;
    amount_type?: AmountTypeEnum;
};
