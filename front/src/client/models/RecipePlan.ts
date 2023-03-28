/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type RecipePlan = {
    readonly id: number;
    day?: number | null;
    date?: string | null;
    week?: number;
    meal_time: number;
    recipe?: number | null;
};
