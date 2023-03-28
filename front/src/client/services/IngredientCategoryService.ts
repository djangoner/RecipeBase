/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { IngredientCategory } from '../models/IngredientCategory';
import type { PaginatedIngredientCategoryList } from '../models/PaginatedIngredientCategoryList';
import type { PatchedIngredientCategory } from '../models/PatchedIngredientCategory';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class IngredientCategoryService {

    /**
     * @returns PaginatedIngredientCategoryList 
     * @throws ApiError
     */
    public static ingredientCategoryList({
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
}): CancelablePromise<PaginatedIngredientCategoryList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ingredient_category/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns IngredientCategory 
     * @throws ApiError
     */
    public static ingredientCategoryCreate({
requestBody,
}: {
requestBody: IngredientCategory,
}): CancelablePromise<IngredientCategory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ingredient_category/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns IngredientCategory 
     * @throws ApiError
     */
    public static ingredientCategoryRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Категория ингредиента.
 */
id: number,
}): CancelablePromise<IngredientCategory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ingredient_category/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns IngredientCategory 
     * @throws ApiError
     */
    public static ingredientCategoryUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Категория ингредиента.
 */
id: number,
requestBody: IngredientCategory,
}): CancelablePromise<IngredientCategory> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/ingredient_category/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns IngredientCategory 
     * @throws ApiError
     */
    public static ingredientCategoryPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Категория ингредиента.
 */
id: number,
requestBody?: PatchedIngredientCategory,
}): CancelablePromise<IngredientCategory> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/ingredient_category/{id}/',
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
    public static ingredientCategoryDestroy({
id,
}: {
/**
 * A unique integer value identifying this Категория ингредиента.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/ingredient_category/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
