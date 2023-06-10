/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type RecipePlan = {
    readonly id: number;
    day?: number | null;
    date?: string | null;
    readonly created: string;
    week?: number;
    meal_time: number;
    recipe?: number | null;
};
