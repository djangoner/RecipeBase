/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type ConditionWarning = {
    condition: number;
    value_current: string;
    value_expected: string;
    plan: number;
    childrens: Array<ConditionWarning>;
};
