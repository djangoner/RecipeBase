/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AmountTypes } from '../models/AmountTypes';
import type { Ingredient } from '../models/Ingredient';
import type { IngredientRead } from '../models/IngredientRead';
import type { PaginatedIngredientReadList } from '../models/PaginatedIngredientReadList';
import type { PatchedIngredient } from '../models/PatchedIngredient';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class IngredientsService {

    /**
     * @returns PaginatedIngredientReadList 
     * @throws ApiError
     */
    public static ingredientsList({
category,
categoryIsnull,
edible,
expand,
fields,
needBuy,
omit,
ordering,
page,
pageSize,
priceIsnull,
recipesIsnull,
search,
}: {
category?: number,
categoryIsnull?: boolean,
edible?: boolean,
/**
 * Which field should be expanded, comma separated
 */
expand?: string,
/**
 * Which fields should be returned
 */
fields?: string,
needBuy?: boolean,
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
priceIsnull?: boolean,
recipesIsnull?: boolean,
/**
 * A search term.
 */
search?: string,
}): CancelablePromise<PaginatedIngredientReadList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ingredients/',
            query: {
                'category': category,
                'category__isnull': categoryIsnull,
                'edible': edible,
                'expand': expand,
                'fields': fields,
                'need_buy': needBuy,
                'omit': omit,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'price__isnull': priceIsnull,
                'recipes__isnull': recipesIsnull,
                'search': search,
            },
        });
    }

    /**
     * @returns IngredientRead 
     * @throws ApiError
     */
    public static ingredientsCreate({
requestBody,
}: {
requestBody: Ingredient,
}): CancelablePromise<IngredientRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ingredients/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns IngredientRead 
     * @throws ApiError
     */
    public static ingredientsRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Ингредиент.
 */
id: number,
}): CancelablePromise<IngredientRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ingredients/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns IngredientRead 
     * @throws ApiError
     */
    public static ingredientsUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Ингредиент.
 */
id: number,
requestBody: Ingredient,
}): CancelablePromise<IngredientRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/ingredients/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns IngredientRead 
     * @throws ApiError
     */
    public static ingredientsPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Ингредиент.
 */
id: number,
requestBody?: PatchedIngredient,
}): CancelablePromise<IngredientRead> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/ingredients/{id}/',
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
    public static ingredientsDestroy({
id,
}: {
/**
 * A unique integer value identifying this Ингредиент.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/ingredients/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns AmountTypes 
     * @throws ApiError
     */
    public static ingredientsAmountTypesRetrieve(): CancelablePromise<AmountTypes> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ingredients/amount_types/',
        });
    }

}
