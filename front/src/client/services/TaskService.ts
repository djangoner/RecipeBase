/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedTaskNestedList } from '../models/PaginatedTaskNestedList';
import type { PatchedTaskNested } from '../models/PatchedTaskNested';
import type { TaskNested } from '../models/TaskNested';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TaskService {

    /**
     * @returns PaginatedTaskNestedList 
     * @throws ApiError
     */
    public static taskList({
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
}): CancelablePromise<PaginatedTaskNestedList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/task/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns TaskNested 
     * @throws ApiError
     */
    public static taskCreate({
requestBody,
}: {
requestBody: TaskNested,
}): CancelablePromise<TaskNested> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/task/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns TaskNested 
     * @throws ApiError
     */
    public static taskRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Задача.
 */
id: number,
}): CancelablePromise<TaskNested> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/task/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns TaskNested 
     * @throws ApiError
     */
    public static taskUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Задача.
 */
id: number,
requestBody: TaskNested,
}): CancelablePromise<TaskNested> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/task/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns TaskNested 
     * @throws ApiError
     */
    public static taskPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Задача.
 */
id: number,
requestBody?: PatchedTaskNested,
}): CancelablePromise<TaskNested> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/task/{id}/',
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
    public static taskDestroy({
id,
}: {
/**
 * A unique integer value identifying this Задача.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/task/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
