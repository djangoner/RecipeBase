/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedProductListWeekReadList } from '../models/PaginatedProductListWeekReadList';
import type { PatchedProductListWeek } from '../models/PatchedProductListWeek';
import type { ProductListWeek } from '../models/ProductListWeek';
import type { ProductListWeekRead } from '../models/ProductListWeekRead';
import type { StatusOk } from '../models/StatusOk';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ProductListWeekService {

    /**
     * @returns PaginatedProductListWeekReadList 
     * @throws ApiError
     */
    public static productListWeekList({
expand,
fields,
omit,
ordering,
page,
pageSize,
search,
}: {
/**
 * Which field should be expanded, comma separated
 */
expand?: string,
/**
 * Which fields should be returned
 */
fields?: string,
/**
 * Which fields should be excluded from results
 */
omit?: string,
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
}): CancelablePromise<PaginatedProductListWeekReadList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/',
            query: {
                'expand': expand,
                'fields': fields,
                'omit': omit,
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
     * @returns ProductListWeekRead 
     * @throws ApiError
     */
    public static productListWeekRetrieve({
id,
}: {
id: string,
}): CancelablePromise<ProductListWeekRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ProductListWeekRead 
     * @throws ApiError
     */
    public static productListWeekUpdate({
id,
requestBody,
}: {
id: string,
requestBody: ProductListWeek,
}): CancelablePromise<ProductListWeekRead> {
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
     * @returns ProductListWeekRead 
     * @throws ApiError
     */
    public static productListWeekPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Список покупок недели.
 */
id: number,
requestBody?: PatchedProductListWeek,
}): CancelablePromise<ProductListWeekRead> {
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
     * @returns ProductListWeekRead 
     * @throws ApiError
     */
    public static productListWeekGenerateRetrieve({
id,
}: {
id: string,
}): CancelablePromise<ProductListWeekRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/generate/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns StatusOk 
     * @throws ApiError
     */
    public static productListWeekMoveUncompletedRetrieve({
id,
}: {
id: string,
}): CancelablePromise<StatusOk> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/move_uncompleted/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns StatusOk 
     * @throws ApiError
     */
    public static productListWeekSendListRetrieve({
id,
}: {
id: string,
}): CancelablePromise<StatusOk> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/send_list/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns StatusOk 
     * @throws ApiError
     */
    public static productListWeekSendSyncedRetrieve({
id,
}: {
id: string,
}): CancelablePromise<StatusOk> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_week/{id}/send_synced/',
            path: {
                'id': id,
            },
        });
    }

}
