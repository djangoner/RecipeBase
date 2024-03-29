/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeImage } from './RecipeImage';
import type { RecipeIngredient } from './RecipeIngredient';
import type { RecipeRating } from './RecipeRating';
import type { RecipeTag } from './RecipeTag';
import type { ShortUser } from './ShortUser';

/**
 * A ModelSerializer that takes additional arguments for
 * "fields", "omit" and "expand" in order to
 * control which fields are displayed, and whether to replace simple
 * values with complex, nested serializations
 */
export type Recipe = {
    readonly id: number;
    readonly short_description_str: string;
    readonly last_cooked: string;
    readonly cooked_times: number;
    readonly is_planned: boolean;
    images?: Array<RecipeImage>;
    tags?: Array<RecipeTag>;
    ingredients?: Array<RecipeIngredient>;
    ratings?: Array<RecipeRating>;
    readonly author: ShortUser;
    title: string;
    content?: string;
    content_source?: string;
    short_description?: string | null;
    comment?: string | null;
    portion_count?: number | null;
    cooking_time?: number | null;
    preparation_time?: number | null;
    source_link?: string | null;
    readonly created: string | null;
    readonly edited: string | null;
    is_archived?: boolean;
};
