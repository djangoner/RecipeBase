/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ConditionWarning } from './ConditionWarning';
import type { RecipeIngredientRecommendation } from './RecipeIngredientRecommendation';
import type { RecipePlanShort } from './RecipePlanShort';

export type PatchedRecipePlanWeek = {
    readonly id?: number;
    plans?: Array<RecipePlanShort>;
    readonly warnings?: Array<ConditionWarning>;
    readonly edited_first?: string;
    readonly edited_last?: string;
    readonly recommendations_ingredients?: Array<RecipeIngredientRecommendation>;
    year?: number;
    week?: number;
    comments?: Record<string, any>;
    is_filled?: boolean;
};
