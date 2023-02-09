/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TaskNested } from './TaskNested';

export type PaginatedTaskNestedList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<TaskNested>;
};
