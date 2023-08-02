def week_delta(year: int, week: int, delta: int):
    """Add delta weeks to year & week"""
    week += delta

    if week < 0:
        week = 53
    if week > 54:
        week = 1

    return year, week
