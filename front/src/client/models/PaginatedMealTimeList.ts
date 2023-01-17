/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MealTime } from './MealTime';

export type PaginatedMealTimeList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<MealTime>;
};
