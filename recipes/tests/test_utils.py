from datetime import date, datetime


from recipes.services.utils import get_first_weekday


def test_get_first_weekday():
    assert get_first_weekday(datetime(2023, 1, 2)) == date(2023, 1, 2)
    assert get_first_weekday(datetime(2023, 1, 3)) == date(2023, 1, 2)
    assert get_first_weekday(datetime(2023, 1, 4)) == date(2023, 1, 2)
    assert get_first_weekday(datetime(2023, 1, 5)) == date(2023, 1, 2)
    assert get_first_weekday(datetime(2023, 1, 6)) == date(2023, 1, 2)
    assert get_first_weekday(datetime(2023, 1, 7)) == date(2023, 1, 9)
    assert get_first_weekday(datetime(2023, 1, 8)) == date(2023, 1, 9)
