import logging
import random
from typing import TypeVar
from django.db.models import Max

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


def get_random_obj_from_queryset(queryset, maxtry: int = 5):
    if queryset.count() < 100:
        return queryset.order_by("?")[0]
    max_pk = queryset.aggregate(max_pk=Max("pk"))["max_pk"]
    for _ in range(maxtry):
        obj = queryset.filter(pk=random.randint(1, max_pk)).first()
        if obj:
            logging.info(f"Random obj hit: {obj}")
            return obj
        else:
            logging.info("Random obj miss...")
