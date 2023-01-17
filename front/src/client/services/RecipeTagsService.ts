/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipeTagList } from '../models/PaginatedRecipeTagList';
import type { PatchedRecipeTag } from '../models/PatchedRecipeTag';
import type { RecipeTag } from '../models/RecipeTag';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipeTagsService {

    /**
     * @returns PaginatedRecipeTagList 
     * @throws ApiError
     */
    public static recipeTagsList({
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
}): CancelablePromise<PaginatedRecipeTagList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_tags/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }

    /**
     * @returns RecipeTag 
     * @throws ApiError
     */
    public static recipeTagsCreate({
requestBody,
}: {
requestBody: RecipeTag,
}): CancelablePromise<RecipeTag> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipe_tags/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeTag 
     * @throws ApiError
     */
    public static recipeTagsRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Метка рецепта.
 */
id: number,
}): CancelablePromise<RecipeTag> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipe_tags/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipeTag 
     * @throws ApiError
     */
    public static recipeTagsUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Метка рецепта.
 */
id: number,
requestBody: RecipeTag,
}): CancelablePromise<RecipeTag> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipe_tags/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeTag 
     * @throws ApiError
     */
    public static recipeTagsPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Метка рецепта.
 */
id: number,
requestBody?: PatchedRecipeTag,
}): CancelablePromise<RecipeTag> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipe_tags/{id}/',
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
    public static recipeTagsDestroy({
id,
}: {
/**
 * A unique integer value identifying this Метка рецепта.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipe_tags/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
