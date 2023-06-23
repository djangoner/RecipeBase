/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConditionWarning } from '../models/ConditionWarning';
import type { PaginatedRecipePlanWeekReadList } from '../models/PaginatedRecipePlanWeekReadList';
import type { PatchedRecipePlanWeek } from '../models/PatchedRecipePlanWeek';
import type { RecipePlanWeek } from '../models/RecipePlanWeek';
import type { RecipePlanWeekRead } from '../models/RecipePlanWeekRead';
import type { Recommendations } from '../models/Recommendations';
import type { StatusOk } from '../models/StatusOk';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipePlanWeekService {

    /**
     * @returns PaginatedRecipePlanWeekReadList 
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
}): CancelablePromise<PaginatedRecipePlanWeekReadList> {
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
     * @returns RecipePlanWeekRead 
     * @throws ApiError
     */
    public static recipePlanWeekRetrieve({
id,
}: {
id: string,
}): CancelablePromise<RecipePlanWeekRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipePlanWeekRead 
     * @throws ApiError
     */
    public static recipePlanWeekUpdate({
id,
requestBody,
}: {
id: string,
requestBody: RecipePlanWeek,
}): CancelablePromise<RecipePlanWeekRead> {
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
     * @returns RecipePlanWeekRead 
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
}): CancelablePromise<RecipePlanWeekRead> {
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

    /**
     * @returns StatusOk 
     * @throws ApiError
     */
    public static recipePlanWeekRecommendationAcceptCreate({
id,
recommendation,
}: {
id: string,
recommendation?: string,
}): CancelablePromise<StatusOk> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_plan_week/{id}/recommendation_accept/',
            path: {
                'id': id,
            },
            query: {
                'recommendation': recommendation,
            },
        });
    }

    /**
     * @returns StatusOk 
     * @throws ApiError
     */
    public static recipePlanWeekRecommendationCancelCreate({
id,
recommendation,
}: {
id: string,
recommendation?: string,
}): CancelablePromise<StatusOk> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_plan_week/{id}/recommendation_cancel/',
            path: {
                'id': id,
            },
            query: {
                'recommendation': recommendation,
            },
        });
    }

    /**
     * @returns Recommendations 
     * @throws ApiError
     */
    public static recipePlanWeekRecommendationsRetrieve({
id,
}: {
id: string,
}): CancelablePromise<Recommendations> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan_week/{id}/recommendations/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ConditionWarning 
     * @throws ApiError
     */
    public static recipePlanWeekWarningsRetrieve({
id,
}: {
id: string,
}): CancelablePromise<ConditionWarning> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_plan_week/{id}/warnings/',
            path: {
                'id': id,
            },
        });
    }

}
