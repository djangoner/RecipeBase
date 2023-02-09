/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type MealTime = {
    readonly id: number;
    title: string;
    time?: string | null;
    num?: number | null;
    /**
     * Является ли прием пищи основным (обязательным на каждый день)
     */
    is_primary?: boolean;
};
