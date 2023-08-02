/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';

export type RegularIngredient = {
    readonly id: number;
    readonly amount_type_str: string;
    day?: number | null;
    amount: number;
    amount_type?: AmountTypeEnum;
    active?: boolean;
    ingredient: number;
};
