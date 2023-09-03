/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeShort } from './RecipeShort';

export type RecipePlanShort = {
    readonly id: number;
    recipe: RecipeShort;
    day?: number | null;
    date?: string | null;
    readonly created: string;
    week?: number;
    meal_time: number;
};
