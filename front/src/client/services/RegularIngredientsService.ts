/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRegularIngredientList } from '../models/PaginatedRegularIngredientList';
import type { PatchedRegularIngredient } from '../models/PatchedRegularIngredient';
import type { RegularIngredient } from '../models/RegularIngredient';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RegularIngredientsService {

    /**
     * @returns PaginatedRegularIngredientList 
     * @throws ApiError
     */
    public static regularIngredientsList({
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
}): CancelablePromise<PaginatedRegularIngredientList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/regular_ingredients/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RegularIngredient 
     * @throws ApiError
     */
    public static regularIngredientsCreate({
requestBody,
}: {
requestBody: RegularIngredient,
}): CancelablePromise<RegularIngredient> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/regular_ingredients/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RegularIngredient 
     * @throws ApiError
     */
    public static regularIngredientsRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Регулярный ингредиент.
 */
id: number,
}): CancelablePromise<RegularIngredient> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/regular_ingredients/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RegularIngredient 
     * @throws ApiError
     */
    public static regularIngredientsUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Регулярный ингредиент.
 */
id: number,
requestBody: RegularIngredient,
}): CancelablePromise<RegularIngredient> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/regular_ingredients/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RegularIngredient 
     * @throws ApiError
     */
    public static regularIngredientsPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Регулярный ингредиент.
 */
id: number,
requestBody?: PatchedRegularIngredient,
}): CancelablePromise<RegularIngredient> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/regular_ingredients/{id}/',
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
    public static regularIngredientsDestroy({
id,
}: {
/**
 * A unique integer value identifying this Регулярный ингредиент.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/regular_ingredients/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
