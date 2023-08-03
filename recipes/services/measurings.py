import logging
from typing import Tuple, TypeAlias
from django.utils.translation import gettext_lazy as _

IngredientAmounts: TypeAlias = list[tuple[str, int | float | None]]

MEASURING_TYPES = (
    ("g", _("Граммы")),
    ("kg", _("Килограммы")),
    ("l", _("Литры")),
    ("ml", _("Миллилитры")),
    ("cup", _("Стакан")),
    ("pinch", _("Щепотка")),
    ("table_spoon", _("Ст. Л.")),
    ("tea_spoon", _("Ч. Л.")),
    ("head", _("Качан")),
    ("items", _("Шт")),
    ("fl_oz", _("fl oz")),
)

MEASURING_TRANSLATES = {
    "oz": "fl_oz",
    "fl_oz": "fl_oz",
    "г": "g",
    "гр": "g",
    "грамм": "g",
    "шт": "items",
    "зуб": "items",
    "стл": "table_spoon",
    "чл": "tea_spoon",
    "чаш": "cup",
    "чашка": "cup",
    "стакан": "cup",
}

MEASURING_SHORT = {"g": "гр", "kg": "кг", "l": "л", "ml": "мл", "items": "шт"}

MEASURING_CONVERT = {
    # meas: gramm_count
    "g": 1,
    "kg": 1000,
    "cup": 250,
    "pinch": 2,
    "table_spoon": 20,
    "tea_spoon": 10,
    "fl_oz": 30,
}

MEASURING_LIQUIDS = ["l", "ml", "fl_oz", "g"]
CONVERT_ADVANCED = ["l", "ml"]

MEAS_TYPES_DICT = dict(MEASURING_TYPES)
MEAS_TYPES_DICT_REVERSED = {v.lower(): k.lower() for k, v in MEAS_TYPES_DICT.items()}


def short_text(tx: str, length: int = 100):
    if len(tx) < length:
        return tx

    return tx[:length] + "..."


def amount_to_grams(amount: int | float | None, measure: str) -> int | None:
    multiplier = MEASURING_CONVERT.get(measure)

    if not multiplier or not amount:
        return None

    return int(amount * multiplier)


def measuring_str(meas: str | None):
    meas_types = dict(MEASURING_TYPES)
    if meas in MEASURING_SHORT:
        return str(MEASURING_SHORT[meas])
    elif meas in meas_types:
        return str(meas_types[meas])

    return meas


def is_convertible(measuring: str, advanced: bool = True) -> bool:
    return measuring in MEASURING_CONVERT or (advanced and measuring in CONVERT_ADVANCED)


def translate_measuring(meas: str):
    if meas in MEASURING_TRANSLATES:
        return MEASURING_TRANSLATES.get(meas, None)
    elif meas in MEAS_TYPES_DICT:
        return meas
    elif meas in MEAS_TYPES_DICT_REVERSED:
        return MEAS_TYPES_DICT_REVERSED[meas]


def convert_all_to_grams(measurings: IngredientAmounts) -> Tuple[str, int | float]:
    res: float = 0
    all_meas = "g"

    non_empty = list(filter(lambda m: m[1], measurings))
    all_liquids = all([meas in MEASURING_LIQUIDS for meas, amount in non_empty])
    all_grams = all([meas == "g" for meas, amount in non_empty])
    all_normal = all([is_convertible(meas, advanced=False) for meas, amount in non_empty])

    for meas, amount in measurings:
        if not amount:
            continue

        if all_liquids and not all_grams:
            if meas == "l":
                res += amount * 1000
                all_meas = "ml"
            elif meas in ["ml", "g"]:
                res += amount
                all_meas = "ml"
            else:
                logging.debug(f"[liquids]Invalid measuring: {meas}")  # pragma: no cover
        elif all_normal:
            if is_convertible(meas, advanced=False):
                amount_grams = amount_to_grams(amount, meas)
                if amount_grams:
                    res += amount_grams
            # elif meas == "items":
            #     res += amount
            else:
                logging.debug(f"[grams]Invalid measuring: {meas}")  # pragma: no cover
        else:
            logging.debug(f"[mixed]Invalid measuring: {meas}")

    return all_meas, res
