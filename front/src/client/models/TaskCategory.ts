/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Task } from './Task';

export type TaskCategory = {
    readonly id: number;
    readonly childrens: Array<Task>;
    title: string;
    description?: string | null;
    icon?: string | null;
    sort?: number | null;
    readonly created: string;
    author?: number | null;
};
