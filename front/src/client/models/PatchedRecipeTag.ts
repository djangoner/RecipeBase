/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeTagTypeEnum } from './RecipeTagTypeEnum';

/**
 * Adds nested create feature
 */
export type PatchedRecipeTag = {
    readonly id?: number;
    title?: string;
    type?: RecipeTagTypeEnum;
};
