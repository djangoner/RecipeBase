/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipeRatingList } from '../models/PaginatedRecipeRatingList';
import type { PatchedRecipeRating } from '../models/PatchedRecipeRating';
import type { RecipeRating } from '../models/RecipeRating';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipeRatingService {

    /**
     * @returns PaginatedRecipeRatingList 
     * @throws ApiError
     */
    public static recipeRatingList({
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
}): CancelablePromise<PaginatedRecipeRatingList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_rating/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RecipeRating 
     * @throws ApiError
     */
    public static recipeRatingCreate({
requestBody,
}: {
requestBody: RecipeRating,
}): CancelablePromise<RecipeRating> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_rating/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeRating 
     * @throws ApiError
     */
    public static recipeRatingRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Оценка рецепта.
 */
id: number,
}): CancelablePromise<RecipeRating> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_rating/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipeRating 
     * @throws ApiError
     */
    public static recipeRatingUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Оценка рецепта.
 */
id: number,
requestBody: RecipeRating,
}): CancelablePromise<RecipeRating> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipe_rating/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeRating 
     * @throws ApiError
     */
    public static recipeRatingPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Оценка рецепта.
 */
id: number,
requestBody?: PatchedRecipeRating,
}): CancelablePromise<RecipeRating> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipe_rating/{id}/',
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
    public static recipeRatingDestroy({
id,
}: {
/**
 * A unique integer value identifying this Оценка рецепта.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipe_rating/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
