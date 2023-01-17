/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedProductListWeekList } from '../models/PaginatedProductListWeekList';
import type { PatchedProductListWeek } from '../models/PatchedProductListWeek';
import type { ProductListWeek } from '../models/ProductListWeek';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ProductListWeekService {

    /**
     * @returns PaginatedProductListWeekList 
     * @throws ApiError
     */
    public static productListWeekList({
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
}): CancelablePromise<PaginatedProductListWeekList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns ProductListWeek 
     * @throws ApiError
     */
    public static productListWeekCreate({
requestBody,
}: {
requestBody: ProductListWeek,
}): CancelablePromise<ProductListWeek> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/product_list_week/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns ProductListWeek 
     * @throws ApiError
     */
    public static productListWeekRetrieve({
id,
}: {
id: string,
}): CancelablePromise<ProductListWeek> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ProductListWeek 
     * @throws ApiError
     */
    public static productListWeekUpdate({
id,
requestBody,
}: {
id: string,
requestBody: ProductListWeek,
}): CancelablePromise<ProductListWeek> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/product_list_week/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns ProductListWeek 
     * @throws ApiError
     */
    public static productListWeekPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Список продуктов недели.
 */
id: number,
requestBody?: PatchedProductListWeek,
}): CancelablePromise<ProductListWeek> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/product_list_week/{id}/',
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
    public static productListWeekDestroy({
id,
}: {
id: string,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/product_list_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ProductListWeek 
     * @throws ApiError
     */
    public static productListWeekGenerateRetrieve({
id,
}: {
id: string,
}): CancelablePromise<ProductListWeek> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/generate/',
            path: {
                'id': id,
            },
        });
    }

}
