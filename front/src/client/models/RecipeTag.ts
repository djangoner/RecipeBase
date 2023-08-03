/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeTagTypeEnum } from './RecipeTagTypeEnum';

/**
 * Adds nested create feature
 */
export type RecipeTag = {
    readonly id: number;
    title: string;
    type?: RecipeTagTypeEnum;
};
