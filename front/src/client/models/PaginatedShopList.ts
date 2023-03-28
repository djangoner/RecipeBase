/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Shop } from './Shop';

export type PaginatedShopList = {
    count?: number;
    next?: string | null;
    previous?: string | null;
    results?: Array<Shop>;
};
