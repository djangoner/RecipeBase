/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TaskCategory } from './TaskCategory';

export type PaginatedTaskCategoryList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<TaskCategory>;
};
