/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedWeekPlanConditionList } from '../models/PaginatedWeekPlanConditionList';
import type { PatchedWeekPlanCondition } from '../models/PatchedWeekPlanCondition';
import type { WeekPlanCondition } from '../models/WeekPlanCondition';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ConditionsService {

    /**
     * @returns PaginatedWeekPlanConditionList 
     * @throws ApiError
     */
    public static conditionsList({
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
}): CancelablePromise<PaginatedWeekPlanConditionList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conditions/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns WeekPlanCondition 
     * @throws ApiError
     */
    public static conditionsCreate({
requestBody,
}: {
requestBody?: WeekPlanCondition,
}): CancelablePromise<WeekPlanCondition> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/conditions/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns WeekPlanCondition 
     * @throws ApiError
     */
    public static conditionsRetrieve({
id,
}: {
/**
 * A unique integer value identifying this week plan condition.
 */
id: number,
}): CancelablePromise<WeekPlanCondition> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conditions/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns WeekPlanCondition 
     * @throws ApiError
     */
    public static conditionsUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this week plan condition.
 */
id: number,
requestBody?: WeekPlanCondition,
}): CancelablePromise<WeekPlanCondition> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/conditions/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns WeekPlanCondition 
     * @throws ApiError
     */
    public static conditionsPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this week plan condition.
 */
id: number,
requestBody?: PatchedWeekPlanCondition,
}): CancelablePromise<WeekPlanCondition> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/conditions/{id}/',
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
    public static conditionsDestroy({
id,
}: {
/**
 * A unique integer value identifying this week plan condition.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/conditions/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
