/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';

export type RecipeIngredientRecommendation = {
    readonly id: number;
    ingredient?: number | null;
    readonly amount_type_str: string;
    amount: number;
    amount_type?: AmountTypeEnum;
    recipe?: number;
};
