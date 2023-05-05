/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ShortUser } from './ShortUser';

export type RecipeRatingRead = {
    readonly id: number;
    user: ShortUser;
    rating?: number | null;
    recipe?: number;
};
