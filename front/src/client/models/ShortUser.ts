/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Nested } from './Nested';

export type ShortUser = {
    readonly id: number;
    password: string;
    /**
     * Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.
     */
    username: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Отметьте, если пользователь должен считаться активным. Уберите эту отметку вместо удаления учётной записи.
     */
    is_active?: boolean;
    readonly groups: Array<Nested>;
    readonly user_permissions: Array<Nested>;
};
