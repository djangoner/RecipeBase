/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type Nested = {
    readonly id: number;
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
    readonly price_part: number;
    readonly price_full: number;
    readonly author: Nested;
    readonly tags: Array<Nested>;
    readonly recommendations_recipes: Array<Nested>;
    readonly recommendations_tags: Array<Nested>;
};
