/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipeImageList } from '../models/PaginatedRecipeImageList';
import type { PatchedRecipeImage } from '../models/PatchedRecipeImage';
import type { RecipeImage } from '../models/RecipeImage';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipeImagesService {

    /**
     * @returns PaginatedRecipeImageList 
     * @throws ApiError
     */
    public static recipeImagesList({
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
}): CancelablePromise<PaginatedRecipeImageList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_images/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RecipeImage 
     * @throws ApiError
     */
    public static recipeImagesCreate({
requestBody,
}: {
requestBody: RecipeImage,
}): CancelablePromise<RecipeImage> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_images/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeImage 
     * @throws ApiError
     */
    public static recipeImagesRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Изображение рецепта.
 */
id: number,
}): CancelablePromise<RecipeImage> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_images/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipeImage 
     * @throws ApiError
     */
    public static recipeImagesUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Изображение рецепта.
 */
id: number,
requestBody: RecipeImage,
}): CancelablePromise<RecipeImage> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipe_images/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeImage 
     * @throws ApiError
     */
    public static recipeImagesPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Изображение рецепта.
 */
id: number,
requestBody?: PatchedRecipeImage,
}): CancelablePromise<RecipeImage> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipe_images/{id}/',
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
    public static recipeImagesDestroy({
id,
}: {
/**
 * A unique integer value identifying this Изображение рецепта.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipe_images/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
