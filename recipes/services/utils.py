from typing import TypeVar

T = TypeVar("T")


def week_delta(year: int, week: int, delta: int):
    """Add delta weeks to year & week"""
    week += delta

    if week < 0:
        week = 53
    if week > 54:
        week = 1

    return year, week


def first_or_none(lst: list[T] | None) -> T | None:
    return next(iter(lst or []), None)
