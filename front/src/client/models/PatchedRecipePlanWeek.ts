/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ConditionWarning } from './ConditionWarning';
import type { RecipePlanShort } from './RecipePlanShort';

/**
 * Adds nested create feature
 */
export type PatchedRecipePlanWeek = {
    readonly id?: number;
    plans?: Array<RecipePlanShort>;
    readonly warnings?: Array<ConditionWarning>;
    year?: number;
    week?: number;
    comments?: Record<string, any>;
    is_filled?: boolean;
};
