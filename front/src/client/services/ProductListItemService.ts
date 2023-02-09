/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedProductListItemReadList } from '../models/PaginatedProductListItemReadList';
import type { PatchedProductListItem } from '../models/PatchedProductListItem';
import type { ProductListItem } from '../models/ProductListItem';
import type { ProductListItemRead } from '../models/ProductListItemRead';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ProductListItemService {

    /**
     * @returns PaginatedProductListItemReadList 
     * @throws ApiError
     */
    public static productListItemList({
isAuto,
isCompleted,
isDeleted,
ordering,
page,
pageSize,
search,
}: {
isAuto?: boolean,
isCompleted?: boolean,
isDeleted?: boolean,
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
}): CancelablePromise<PaginatedProductListItemReadList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_item/',
            query: {
                'is_auto': isAuto,
                'is_completed': isCompleted,
                'is_deleted': isDeleted,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns ProductListItemRead 
     * @throws ApiError
     */
    public static productListItemCreate({
requestBody,
}: {
requestBody: ProductListItem,
}): CancelablePromise<ProductListItemRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/product_list_item/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns ProductListItemRead 
     * @throws ApiError
     */
    public static productListItemRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Список покупок.
 */
id: number,
}): CancelablePromise<ProductListItemRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/product_list_item/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ProductListItemRead 
     * @throws ApiError
     */
    public static productListItemUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Список покупок.
 */
id: number,
requestBody: ProductListItem,
}): CancelablePromise<ProductListItemRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/product_list_item/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns ProductListItem 
     * @throws ApiError
     */
    public static productListItemPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Список покупок.
 */
id: number,
requestBody?: PatchedProductListItem,
}): CancelablePromise<ProductListItem> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/product_list_item/{id}/',
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
    public static productListItemDestroy({
id,
}: {
/**
 * A unique integer value identifying this Список покупок.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/product_list_item/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns ProductListItem 
     * @throws ApiError
     */
    public static productListItemMoveWeekCreate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Список покупок.
 */
id: number,
requestBody: ProductListItem,
}): CancelablePromise<ProductListItem> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/product_list_item/{id}/move_week/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

}
