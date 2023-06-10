/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRecipeReadList } from '../models/PaginatedRecipeReadList';
import type { PatchedRecipe } from '../models/PatchedRecipe';
import type { Recipe } from '../models/Recipe';
import type { RecipeRead } from '../models/RecipeRead';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecipesService {

    /**
     * @returns PaginatedRecipeReadList 
     * @throws ApiError
     */
    public static recipesList({
author,
comment,
compilation,
content,
contentSource,
cookingTime,
cookingTimeGt,
cookingTimeLt,
created,
edited,
expand,
fields,
ingredientsExclude,
ingredientsInclude,
isArchived,
omit,
ordering,
page,
pageSize,
portionCount,
preparationTime,
priceFull,
pricePart,
rating,
search,
shortDescription,
sourceLink,
tagsExclude,
tagsInclude,
title,
}: {
author?: number,
comment?: string,
/**
 * Compilation filter
 */
compilation?: string,
content?: string,
contentSource?: string,
cookingTime?: number,
cookingTimeGt?: number,
cookingTimeLt?: number,
created?: string,
edited?: string,
/**
 * Which field should be expanded, comma separated
 */
expand?: string,
/**
 * Which fields should be returned
 */
fields?: string,
/**
 * Ingredients exclude
 */
ingredientsExclude?: string,
/**
 * Ingredients include
 */
ingredientsInclude?: string,
isArchived?: boolean,
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
portionCount?: number,
preparationTime?: number,
priceFull?: number,
pricePart?: number,
/**
 * Rating filter
 */
rating?: string,
/**
 * A search term.
 */
search?: string,
shortDescription?: string,
sourceLink?: string,
/**
 * Tags exclude
 */
tagsExclude?: string,
/**
 * Tags include
 */
tagsInclude?: string,
title?: string,
}): CancelablePromise<PaginatedRecipeReadList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipes/',
            query: {
                'author': author,
                'comment': comment,
                'compilation': compilation,
                'content': content,
                'content_source': contentSource,
                'cooking_time': cookingTime,
                'cooking_time_gt': cookingTimeGt,
                'cooking_time_lt': cookingTimeLt,
                'created': created,
                'edited': edited,
                'expand': expand,
                'fields': fields,
                'ingredients_exclude': ingredientsExclude,
                'ingredients_include': ingredientsInclude,
                'is_archived': isArchived,
                'omit': omit,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'portion_count': portionCount,
                'preparation_time': preparationTime,
                'price_full': priceFull,
                'price_part': pricePart,
                'rating': rating,
                'search': search,
                'short_description': shortDescription,
                'source_link': sourceLink,
                'tags_exclude': tagsExclude,
                'tags_include': tagsInclude,
                'title': title,
            },
        });
    }

    /**
     * @returns RecipeRead 
     * @throws ApiError
     */
    public static recipesCreate({
requestBody,
}: {
requestBody: Recipe,
}): CancelablePromise<RecipeRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/recipes/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeRead 
     * @throws ApiError
     */
    public static recipesRetrieve({
id,
}: {
/**
 * A unique integer value identifying this Рецепт.
 */
id: number,
}): CancelablePromise<RecipeRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/recipes/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * @returns RecipeRead 
     * @throws ApiError
     */
    public static recipesUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Рецепт.
 */
id: number,
requestBody: Recipe,
}): CancelablePromise<RecipeRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/recipes/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * @returns RecipeRead 
     * @throws ApiError
     */
    public static recipesPartialUpdate({
id,
requestBody,
}: {
/**
 * A unique integer value identifying this Рецепт.
 */
id: number,
requestBody?: PatchedRecipe,
}): CancelablePromise<RecipeRead> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/recipes/{id}/',
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
    public static recipesDestroy({
id,
}: {
/**
 * A unique integer value identifying this Рецепт.
 */
id: number,
}): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/recipes/{id}/',
            path: {
                'id': id,
            },
        });
    }

}
