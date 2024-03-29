/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { UserProfile } from './UserProfile';

export type PatchedUser = {
    readonly id?: number;
    profile?: UserProfile;
    readonly permissions?: Array<string>;
    readonly last_login?: string | null;
    /**
     * Указывает, что пользователь имеет все права без явного их назначения.
     */
    readonly is_superuser?: boolean;
    /**
     * Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.
     */
    username?: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Отметьте, если пользователь может входить в административную часть сайта.
     */
    readonly is_staff?: boolean;
    /**
     * Отметьте, если пользователь должен считаться активным. Уберите эту отметку вместо удаления учётной записи.
     */
    is_active?: boolean;
    readonly date_joined?: string;
};
