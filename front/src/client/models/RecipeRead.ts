/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeImage } from './RecipeImage';
import type { RecipeIngredientRead } from './RecipeIngredientRead';
import type { RecipeRatingRead } from './RecipeRatingRead';
import type { RecipeTag } from './RecipeTag';
import type { ShortUser } from './ShortUser';

/**
 * Adds nested create feature
 */
export type RecipeRead = {
    readonly id: number;
    readonly short_description_str: string;
    readonly last_cooked: string;
    readonly cooked_times: number;
    readonly is_planned: boolean;
    images?: Array<RecipeImage>;
    tags?: Array<RecipeTag>;
    ingredients?: Array<RecipeIngredientRead>;
    ratings?: Array<RecipeRatingRead>;
    author: ShortUser;
    title: string;
    content?: string;
    content_source?: string;
    short_description?: string | null;
    comment?: string | null;
    portion_count?: number | null;
    cooking_time?: number | null;
    source_link?: string | null;
    readonly created: string | null;
    readonly edited: string | null;
    is_archived?: boolean;
};