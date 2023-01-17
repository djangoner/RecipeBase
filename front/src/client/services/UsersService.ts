/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedUserList } from '../models/PaginatedUserList';
import type { PatchedUser } from '../models/PatchedUser';
import type { User } from '../models/User';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class UsersService {

    /**
     * @returns PaginatedUserList 
     * @throws ApiError
     */
    public static usersList({
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
}): CancelablePromise<PaginatedUserList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns User 
     * @throws ApiError
     */
    public static usersCreate({
requestBody,
}: {
requestBody: User,
}): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns User 
     * @throws ApiError
     */
    public static usersRetrieve({
id,
}: {
/**
 * A unique integer value identifying this пользователь.
 */
id: number,
}): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns User 
     * @throws ApiError
     */
    public static usersUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this пользователь.
 */
id: number,
requestBody: User,
}): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/users/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns User 
     * @throws ApiError
     */
    public static usersPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this пользователь.
 */
id: number,
requestBody?: PatchedUser,
}): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns User 
     * @throws ApiError
     */
    public static usersCurrentUserInfoRetrieve(): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/current_user_info/',
        });
    }

}
