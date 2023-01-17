/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';

export type RegularIngredient = {
    readonly id: number;
    day?: number | null;
    amount: number;
    amount_type?: AmountTypeEnum;
    ingredient: number;
};
