from django.utils.translation import gettext_lazy as _

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
)

MEASURING_SHORT = {"g": "гр", "kg": "кг", "l": "л", "ml": "мл", "items": "шт"}

MEASURING_CONVERT = {
    # meas: gramm_count
    "g": 1,
    "kg": 1000,
    "cup": 250,
    "pinch": 2,
    "table_spoon": 20,
    "tea_spoon": 10,
}

MEASURING_LIQUIDS = ["l", "ml", "g"]


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
