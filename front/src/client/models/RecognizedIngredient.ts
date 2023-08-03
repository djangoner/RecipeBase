/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Ingredient } from './Ingredient';

export type RecognizedIngredient = {
    ingredient: Ingredient;
    amount: number;
    amount_type: string;
};
