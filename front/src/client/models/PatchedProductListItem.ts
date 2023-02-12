/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AmountTypeEnum } from './AmountTypeEnum';

/**
 * Adds nested create feature
 */
export type PatchedProductListItem = {
    readonly id?: number;
    ingredient?: number | null;
    readonly amount_type_str?: string;
    week?: number;
    readonly packs?: number;
    readonly price_part?: number;
    readonly price_full?: number;
    day?: number | null;
    readonly is_auto?: boolean;
    is_deleted?: boolean;
    is_completed?: boolean;
    title?: string;
    amount?: number | null;
    amount_type?: AmountTypeEnum | null;
    description?: string | null;
    priority?: number;
    readonly created?: string;
    author?: number | null;
    assigned?: number | null;
    readonly ingredients?: Array<number>;
};