/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * * `weekday` - [N] День недели (Число 1-7)
 * * `mtime` - [N] Время приема пищи (ID)
 * * `tag` - [B] Метка рецепта (0/1)
 * * `tag_week` - [N] Кол-во меток на неделе
 * * `ing` - [N] Ингредиент рецепта (кол-во недели)
 * * `ing_main` - [N] Основной ингредиент рецепта (кол-во недели)
 * * `cooking_time` - [N] Время приготовления (кол-во недели)
 * * `minrating` - [N] Мин рейтинг выбранных пользователей (кол-во дня)
 * * `maxrating` - [N] Макс рейтинг выбранных пользователей (кол-во дня)
 * * `duplicates` - [N] дубликатов рецепта (кол-во недели)
 */
export enum PlanFieldEnum {
    WEEKDAY = 'weekday',
    MTIME = 'mtime',
    TAG = 'tag',
    TAG_WEEK = 'tag_week',
    ING = 'ing',
    ING_MAIN = 'ing_main',
    COOKING_TIME = 'cooking_time',
    MINRATING = 'minrating',
    MAXRATING = 'maxrating',
    DUPLICATES = 'duplicates',
}
