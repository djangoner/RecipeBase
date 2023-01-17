/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedShopList } from '../models/PaginatedShopList';
import type { PatchedShop } from '../models/PatchedShop';
import type { Shop } from '../models/Shop';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ShopService {

    /**
     * @returns PaginatedShopList 
     * @throws ApiError
     */
    public static shopList({
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
}): CancelablePromise<PaginatedShopList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/shop/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns Shop 
     * @throws ApiError
     */
    public static shopCreate({
requestBody,
}: {
requestBody: Shop,
}): CancelablePromise<Shop> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/shop/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns Shop 
     * @throws ApiError
     */
    public static shopRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Магазин.
 */
id: number,
}): CancelablePromise<Shop> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/shop/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns Shop 
     * @throws ApiError
     */
    public static shopUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Магазин.
 */
id: number,
requestBody: Shop,
}): CancelablePromise<Shop> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/shop/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns Shop 
     * @throws ApiError
     */
    public static shopPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Магазин.
 */
id: number,
requestBody?: PatchedShop,
}): CancelablePromise<Shop> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/shop/{id}/',
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
    public static shopDestroy({
id,
}: {
/**
 * A unique integer value identifying this Магазин.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/shop/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
