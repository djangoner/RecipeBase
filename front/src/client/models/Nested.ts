/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type Nested = {
    readonly id: number;
    password: string;
    last_login?: string | null;
    /**
     * Указывает, что пользователь имеет все права без явного их назначения.
     */
    is_superuser?: boolean;
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
    is_staff?: boolean;
    /**
     * Отметьте, если пользователь должен считаться активным. Уберите эту отметку вместо удаления учётной записи.
     */
    is_active?: boolean;
    date_joined?: string;
    readonly groups: Array<Nested>;
    readonly user_permissions: Array<Nested>;
};
