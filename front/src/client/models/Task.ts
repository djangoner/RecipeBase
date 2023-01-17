/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TaskNested } from './TaskNested';

export type Task = {
    readonly id: number;
    readonly childrens: Array<TaskNested>;
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
    readonly author: number | null;
    assigned?: number | null;
};
