import datetime
import logging
import random
from typing import TypeVar
from django.db.models import Max
from django.utils import timezone

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


def get_now():
    return timezone.now()


def get_first_weekday(date: datetime.datetime | None = None) -> datetime.date:
    week_firstday = date or get_now().today()
    if week_firstday.weekday() < 5:  # IF monday-friday return this monday
        while week_firstday.weekday() > 0:
            week_firstday = week_firstday - timezone.timedelta(days=1)
    else:
        # Else if saturday-sunday return next monday
        while week_firstday.weekday() > 0:
            week_firstday = week_firstday + timezone.timedelta(days=1)

    return week_firstday.date()
