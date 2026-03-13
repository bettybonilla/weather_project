import asyncio
import logging
import math
import os
from enum import Enum
from typing import Optional

import arrow
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.hourly_weather_aggregate import HourlyWeatherAggregate
from app.services.external.weather_apis.iweather_getter import (
    IWeatherGetter,
    NormalizedWeatherData,
)
from app.services.external.weather_apis.location_api.geocoding import location_data
from app.services.external.weather_apis.nws.weather_data import NWSAPI
from app.services.external.weather_apis.open_meteo.weather_data import OpenMeteoAPI
from app.services.external.weather_apis.weatherapi.weather_data import WeatherAPI

__WEATHER_GETTERS: list[IWeatherGetter] = [
    OpenMeteoAPI(),
    NWSAPI(),
    WeatherAPI(),
]


class TemperatureType(str, Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"


class AggregatedWeatherData(BaseModel):
    avg_temp: int
    avg_rain_prob: int
    unit: TemperatureType = TemperatureType.FAHRENHEIT
    last_updated: str


def use_cache() -> bool:
    """
    Returns True if DEV_BYPASS_CACHE is set to 0 in the environment.
    """
    default_value = True
    dev_bypass_cache = os.getenv("DEV_BYPASS_CACHE")
    if not dev_bypass_cache:
        return default_value

    if dev_bypass_cache not in ("0", "1"):
        return default_value

    return not bool(int(dev_bypass_cache))


def should_fetch(now: arrow.Arrow, db_row: Optional[HourlyWeatherAggregate]) -> bool:
    if db_row is None:
        return True

    if db_row.updated_at.minute < 30 <= now.minute:
        return True
    return False


async def get_aggregated_weather_data(
    requested_zip_code: str, db: AsyncSession = Depends(get_db)
) -> Optional[AggregatedWeatherData]:
    now = arrow.utcnow()

    if use_cache():
        # DB lookup
        async with db.begin():
            stmt = select(HourlyWeatherAggregate).where(
                HourlyWeatherAggregate.zip_code == requested_zip_code,
                HourlyWeatherAggregate.date == now.date(),
                HourlyWeatherAggregate.hour == now.hour,
            )
            result = await db.execute(stmt)
            db_row: Optional[HourlyWeatherAggregate] = result.scalar_one_or_none()

        # Fast path: Found in DB and recent DB data -> Build AggregatedWeatherData from DB
        if not should_fetch(now, db_row):
            updated_at = arrow.get(db_row.updated_at)
            aggregated_weather_data = AggregatedWeatherData(
                avg_temp=db_row.avg_temp,
                avg_rain_prob=db_row.avg_rain_prob,
                last_updated=updated_at.format("YYYY-MM-DDTHH:mm:ssZZ"),
            )
            return aggregated_weather_data

    # Slow path: Not found in DB or should fetch fresh data -> Build AggregatedWeatherData after API calls and upsert
    # into DB
    location_data_result = await location_data.get_location_data(requested_zip_code, db)
    if location_data_result is None:
        logging.getLogger(__name__).error(
            f"Failed to get Geocoding location data for zip code: {requested_zip_code}"
        )
        return None

    tasks = []
    for w in __WEATHER_GETTERS:
        tasks.append(w.get_weather_data(location_data_result))

    weather_data_results = await asyncio.gather(*tasks)
    weather_data_results = list(filter(None, weather_data_results))
    if not weather_data_results:
        return None

    temps: list[float] = []
    rain_probs: list[int] = []
    for r in weather_data_results:
        temps.append(r.temperature)
        rain_probs.append(r.rain_probability)

    avg_temp: int = math.ceil(sum(temps) / len(temps))
    avg_rain_prob: int = math.ceil(sum(rain_probs) / len(rain_probs))

    # Choosing to manually use raw SQL for practice instead of using SQLAlchemy ORM features
    try:
        # Transactional upsert
        # Commits transaction at the end or rolls back if the exception is raised
        async with db.begin():
            tx = text(
                """
                INSERT INTO hourly_weather_aggregates (zip_code, date, hour, avg_temp, avg_rain_prob)
                VALUES (:zip_code, :date, :hour, :avg_temp, :avg_rain_prob)
                ON DUPLICATE KEY UPDATE
                    avg_temp = :avg_temp,
                    avg_rain_prob = :avg_rain_prob,
                    updated_at = :updated_at;
                """
            )
            await db.execute(
                tx,
                {
                    "zip_code": requested_zip_code,
                    "date": now.date(),
                    "hour": now.hour,
                    "avg_temp": avg_temp,
                    "avg_rain_prob": avg_rain_prob,
                    "updated_at": now,
                },
            )
    except SQLAlchemyError as e:
        logging.getLogger(__name__).error(
            f"Error: SQLAlchemyError | Failed to upsert into the hourly_weather_aggregates database table | {e}"
        )
        return None

    aggregated_weather_data = AggregatedWeatherData(
        avg_temp=avg_temp,
        avg_rain_prob=avg_rain_prob,
        last_updated=now.format("YYYY-MM-DDTHH:mm:ssZZ"),
    )
    return aggregated_weather_data


if __name__ == "__main__":
    import random

    class TestWeatherGetter(IWeatherGetter):
        @staticmethod
        async def get_weather_data(
            location_data_result: Optional[location_data.Result],
        ) -> Optional[NormalizedWeatherData]:
            if location_data_result.get_zip_code() != "07310":
                return None

            temperature = random.uniform(0.0, 90.0)
            rain_probability = random.randint(0, 100)
            return NormalizedWeatherData(
                temperature=temperature, rain_probability=rain_probability
            )

    __WEATHER_GETTERS: list[IWeatherGetter] = [
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
    ]

    test_result = asyncio.run(get_aggregated_weather_data("07310"))
    print(test_result)
    print("DONE")
