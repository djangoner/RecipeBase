/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type UserProfile = {
    readonly id: number;
    icon?: string | null;
    num?: number | null;
    show_rate?: boolean;
    conditions_include?: boolean;
    cook_difficulty?: number | null;
    user: number;
    telegram_chat?: number | null;
};
