/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';

export type PatchedRegularIngredient = {
    readonly id?: number;
    day?: number | null;
    amount?: number;
    amount_type?: AmountTypeEnum;
    ingredient?: number;
};
