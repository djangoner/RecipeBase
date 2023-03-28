/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type TaskNested = {
    readonly id: number;
    icon?: string | null;
    is_completed?: boolean;
    title: string;
    description?: string | null;
    priority?: number;
    sort?: number | null;
    deadline?: string | null;
    readonly created: string;
    category: number;
    parent?: number | null;
    author?: number | null;
    assigned?: number | null;
};
