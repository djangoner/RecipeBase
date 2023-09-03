/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Nested } from './Nested';
import type { UserProfile } from './UserProfile';

export type User = {
    readonly id: number;
    profile: UserProfile;
    readonly permissions: Array<string>;
    /**
     * Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.
     */
    username: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Отметьте, если пользователь может входить в административную часть сайта.
     */
    readonly is_staff: boolean;
    /**
     * Отметьте, если пользователь должен считаться активным. Уберите эту отметку вместо удаления учётной записи.
     */
    is_active?: boolean;
    readonly groups: Array<Nested>;
    readonly user_permissions: Array<Nested>;
};
