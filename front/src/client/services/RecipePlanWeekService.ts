/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipePlanWeekList } from '../models/PaginatedRecipePlanWeekList';
import type { PatchedRecipePlanWeek } from '../models/PatchedRecipePlanWeek';
import type { RecipePlanWeek } from '../models/RecipePlanWeek';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipePlanWeekService {

    /**
     * @returns PaginatedRecipePlanWeekList 
     * @throws ApiError
     */
    public static recipePlanWeekList({
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
}): CancelablePromise<PaginatedRecipePlanWeekList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan_week/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RecipePlanWeek 
     * @throws ApiError
     */
    public static recipePlanWeekCreate({
requestBody,
}: {
requestBody: RecipePlanWeek,
}): CancelablePromise<RecipePlanWeek> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_plan_week/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipePlanWeek 
     * @throws ApiError
     */
    public static recipePlanWeekRetrieve({
id,
}: {
id: string,
}): CancelablePromise<RecipePlanWeek> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipePlanWeek 
     * @throws ApiError
     */
    public static recipePlanWeekUpdate({
id,
requestBody,
}: {
id: string,
requestBody: RecipePlanWeek,
}): CancelablePromise<RecipePlanWeek> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipe_plan_week/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipePlanWeek 
     * @throws ApiError
     */
    public static recipePlanWeekPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this План недели.
 */
id: number,
requestBody?: PatchedRecipePlanWeek,
}): CancelablePromise<RecipePlanWeek> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipe_plan_week/{id}/',
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
    public static recipePlanWeekDestroy({
id,
}: {
id: string,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipe_plan_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
