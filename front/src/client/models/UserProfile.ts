/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TelegramNotificationsEnum } from './TelegramNotificationsEnum';

export type UserProfile = {
    readonly id: number;
    icon?: string | null;
    show_rate?: boolean;
    num?: number | null;
    conditions_include?: boolean;
    telegram_id?: string | null;
    telegram_notifications?: TelegramNotificationsEnum | null;
    user: number;
};
