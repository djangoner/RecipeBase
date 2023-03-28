/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StatsList } from '../models/StatsList';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class StatsService {

    /**
     * @returns StatsList 
     * @throws ApiError
     */
    public static statsList(): CancelablePromise<Array<StatsList>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/stats/',
        });
    }

}
