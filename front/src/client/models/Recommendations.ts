/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecipeIngredientRecommendation } from './RecipeIngredientRecommendation';
import type { RecipeRead } from './RecipeRead';
import type { RecipeTag } from './RecipeTag';

export type Recommendations = {
    idx: number;
    hash: string;
    recipe: RecipeRead;
    recipe_tag: RecipeTag;
    ingredient: RecipeIngredientRecommendation;
    plan: number;
};
