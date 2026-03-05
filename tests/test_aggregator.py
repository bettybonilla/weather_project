from typing import Optional

import arrow
import pytest

from app.models.hourly_weather_aggregate import HourlyWeatherAggregate
from app.services.external.weather_apis.aggregator import should_fetch


def mock_data(
    now_minute: int, db_minute: Optional[int]
) -> tuple[arrow.Arrow, Optional[HourlyWeatherAggregate]]:
    now = arrow.get(1971, 1, 1, 5, now_minute, 0)
    if db_minute is None:
        return now, None

    db_row = HourlyWeatherAggregate()
    db_row.updated_at = arrow.get(1971, 1, 1, 5, db_minute, 0)
    return now, db_row


def mock_should_fetch() -> (
    list[tuple[tuple[arrow.Arrow, Optional[HourlyWeatherAggregate]], bool]]
):
    return [
        ((mock_data(now_minute=31, db_minute=None)), True),
        ((mock_data(now_minute=31, db_minute=29)), True),
        ((mock_data(now_minute=30, db_minute=29)), True),
        ((mock_data(now_minute=29, db_minute=25)), False),
        ((mock_data(now_minute=35, db_minute=31)), False),
        ((mock_data(now_minute=31, db_minute=30)), False),
        ((mock_data(now_minute=30, db_minute=30)), False),
        ((mock_data(now_minute=1, db_minute=0)), False),
        ((mock_data(now_minute=59, db_minute=58)), False),
        ((mock_data(now_minute=0, db_minute=0)), False),
    ]


@pytest.mark.parametrize("item, expected", mock_should_fetch())
def test_should_fetch(
    item: tuple[arrow.Arrow, Optional[HourlyWeatherAggregate]], expected: bool
):
    now, db_row = item
    assert should_fetch(now, db_row) == expected
