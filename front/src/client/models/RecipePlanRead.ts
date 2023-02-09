/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MealTime } from './MealTime';
import type { RecipeRead } from './RecipeRead';

export type RecipePlanRead = {
    readonly id: number;
    recipe: RecipeRead;
    meal_time: MealTime;
    day?: number | null;
    date?: string | null;
    week?: number;
};
