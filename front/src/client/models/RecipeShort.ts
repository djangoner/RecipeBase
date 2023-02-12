/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Nested } from './Nested';
import type { RecipeImage } from './RecipeImage';
import type { RecipeIngredient } from './RecipeIngredient';
import type { RecipeRating } from './RecipeRating';

/**
 * Adds nested create feature
 */
export type RecipeShort = {
    readonly id: number;
    readonly short_description_str: string;
    readonly last_cooked: string;
    readonly cooked_times: number;
    readonly is_planned: boolean;
    images?: Array<RecipeImage>;
    ingredients?: Array<RecipeIngredient>;
    ratings?: Array<RecipeRating>;
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
    readonly tags: Array<Nested>;
};
