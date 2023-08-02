/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeIngredientRecommendation } from './RecipeIngredientRecommendation';
import type { RecipeTag } from './RecipeTag';

export type Recommendations = {
    idx: number;
    accepted: boolean;
    hash: string;
    recipe_tag: RecipeTag;
    ingredient: RecipeIngredientRecommendation;
    plan: number;
};
