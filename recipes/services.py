from django.utils.translation import ugettext_lazy as _

MEASURING_TYPES = (
    ('g', _("Граммы")),
    ('cup', _("Стакан")),
    ('pinch', _("Щепотка")),
    ('table_spoon', _("Ст. Л.")),
    ('tea_spoon', _("Ч. Л.")),
)

MEASURING_CONVERT = {
    "g": 1,
    "cup": 250,
    "pinch": 2,
    "table_spoon": 20,
    "tea_spoon": 10,
}
def short_text(tx: str, length: int = 100):
    if len(tx) < length:
        return tx

    return tx[:length] + "..."


def amount_to_grams(amount: int, measure: str) -> int:
    multiplier = MEASURING_CONVERT.get(measure)

    if not multiplier:
        return None

    return int(amount * multiplier)
