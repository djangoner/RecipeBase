/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedTaskCategoryList } from '../models/PaginatedTaskCategoryList';
import type { PatchedTaskCategory } from '../models/PatchedTaskCategory';
import type { TaskCategory } from '../models/TaskCategory';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TaskCategoryService {

    /**
     * @returns PaginatedTaskCategoryList 
     * @throws ApiError
     */
    public static taskCategoryList({
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
}): CancelablePromise<PaginatedTaskCategoryList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/task_category/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns TaskCategory 
     * @throws ApiError
     */
    public static taskCategoryCreate({
requestBody,
}: {
requestBody: TaskCategory,
}): CancelablePromise<TaskCategory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/task_category/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns TaskCategory 
     * @throws ApiError
     */
    public static taskCategoryRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Категория задач.
 */
id: number,
}): CancelablePromise<TaskCategory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/task_category/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns TaskCategory 
     * @throws ApiError
     */
    public static taskCategoryUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Категория задач.
 */
id: number,
requestBody: TaskCategory,
}): CancelablePromise<TaskCategory> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/task_category/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns TaskCategory 
     * @throws ApiError
     */
    public static taskCategoryPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Категория задач.
 */
id: number,
requestBody?: PatchedTaskCategory,
}): CancelablePromise<TaskCategory> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/task_category/{id}/',
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
    public static taskCategoryDestroy({
id,
}: {
/**
 * A unique integer value identifying this Категория задач.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/task_category/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
