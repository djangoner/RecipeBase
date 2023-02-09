/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MealTime } from '../models/MealTime';
import type { PaginatedMealTimeList } from '../models/PaginatedMealTimeList';
import type { PatchedMealTime } from '../models/PatchedMealTime';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class MealTimeService {

    /**
     * @returns PaginatedMealTimeList 
     * @throws ApiError
     */
    public static mealTimeList({
ordering,
page,
pageSize,
search,
}: {
/**
 * Which field to use when ordering the results.
 */
ordering?: string,
/**
 * A page number within the paginated result set.
 */
page?: number,
/**
 * Number of results to return per page.
 */
pageSize?: number,
/**
 * A search term.
 */
search?: string,
}): CancelablePromise<PaginatedMealTimeList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/meal_time/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns MealTime 
     * @throws ApiError
     */
    public static mealTimeCreate({
requestBody,
}: {
requestBody: MealTime,
}): CancelablePromise<MealTime> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/meal_time/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns MealTime 
     * @throws ApiError
     */
    public static mealTimeRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Время приема пищи.
 */
id: number,
}): CancelablePromise<MealTime> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/meal_time/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns MealTime 
     * @throws ApiError
     */
    public static mealTimeUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Время приема пищи.
 */
id: number,
requestBody: MealTime,
}): CancelablePromise<MealTime> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/meal_time/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns MealTime 
     * @throws ApiError
     */
    public static mealTimePartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Время приема пищи.
 */
id: number,
requestBody?: PatchedMealTime,
}): CancelablePromise<MealTime> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/meal_time/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns void 
     * @throws ApiError
     */
    public static mealTimeDestroy({
id,
}: {
/**
 * A unique integer value identifying this Время приема пищи.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/meal_time/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
