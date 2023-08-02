/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeIngredientRecommendation } from './RecipeIngredientRecommendation';
import type { RecipeShort } from './RecipeShort';
import type { RecipeTag } from './RecipeTag';

export type Recommendations = {
    idx: number;
    accepted: boolean;
    hash: string;
    recipe: RecipeShort;
    recipe_tag: RecipeTag;
    ingredient: RecipeIngredientRecommendation;
    plan: number;
};
