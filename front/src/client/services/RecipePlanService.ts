/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipePlanReadList } from '../models/PaginatedRecipePlanReadList';
import type { PatchedRecipePlan } from '../models/PatchedRecipePlan';
import type { RecipePlan } from '../models/RecipePlan';
import type { RecipePlanRead } from '../models/RecipePlanRead';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipePlanService {

    /**
     * @returns PaginatedRecipePlanReadList 
     * @throws ApiError
     */
    public static recipePlanList({
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
}): CancelablePromise<PaginatedRecipePlanReadList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RecipePlan 
     * @throws ApiError
     */
    public static recipePlanCreate({
requestBody,
}: {
requestBody: RecipePlan,
}): CancelablePromise<RecipePlan> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_plan/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipePlanRead 
     * @throws ApiError
     */
    public static recipePlanRetrieve({
id,
}: {
/**
 * A unique integer value identifying this План рецепта.
 */
id: number,
}): CancelablePromise<RecipePlanRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipePlan 
     * @throws ApiError
     */
    public static recipePlanUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this План рецепта.
 */
id: number,
requestBody: RecipePlan,
}): CancelablePromise<RecipePlan> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipe_plan/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipePlan 
     * @throws ApiError
     */
    public static recipePlanPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this План рецепта.
 */
id: number,
requestBody?: PatchedRecipePlan,
}): CancelablePromise<RecipePlan> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipe_plan/{id}/',
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
    public static recipePlanDestroy({
id,
}: {
/**
 * A unique integer value identifying this План рецепта.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipe_plan/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
