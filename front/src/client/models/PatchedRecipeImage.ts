/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Adds nested create feature
 */
export type PatchedRecipeImage = {
    readonly id?: number;
    readonly thumbnails?: Record<string, any>;
    image?: string;
    title?: string | null;
    num?: number | null;
    readonly created?: string | null;
    recipe?: number | null;
};
