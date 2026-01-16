import logging
from typing import Optional

import arrow
import requests
from pydantic import BaseModel, Field, ValidationError

import apis.nws.points_data


class Value(BaseModel):
    value: int


class Period(BaseModel):
    # Date/time format: ISO 8601 ("YYYY-MM-DDTHH:mm:ss±HH:mm")
    start_time: str = Field(alias="startTime")
    # Date/time format: ISO 8601 ("YYYY-MM-DDTHH:mm:ss±HH:mm")
    end_time: str = Field(alias="endTime")
    temperature: float
    # Percentage: 0-100
    rain_probability: Value = Field(alias="probabilityOfPrecipitation")


class Property(BaseModel):
    # List of hourly periods over the next seven days
    periods: list[Period]
    # Default value: "us"
    units: str


class NWSWeatherData(BaseModel):
    properties: Property


# Based on current top of hour (local time)
class SanitizedWeatherData(BaseModel):
    # Date/time format: Arrow object in UTC time ("YYYY-MM-DDTHH:mm:ss+00:00")
    date_time: arrow.arrow.Arrow

    temperature: float

    # Percentage: 0-100
    rain_probability: int

    model_config = {"arbitrary_types_allowed": True}


# TODO: Refactor to implement DRY principle
def get_weather_data(zip_code: str) -> Optional[SanitizedWeatherData]:
    try:
        # noinspection PyProtectedMember
        redirect_url = apis.nws.points_data._get_points_data(zip_code).forecast_hourly
    except AttributeError as e:
        logging.getLogger(__name__).error(
            f"Error: AttributeError | Failed to get redirect URL for zip code: {zip_code}\n{e}"
        )
        return None

    if not redirect_url:
        logging.getLogger(__name__).error(
            f"Failed to get redirect URL for zip code: {zip_code}"
        )
        return None
    response = requests.get(redirect_url, headers={"Accept": "application/geo+json"})
    if response.status_code != 200:
        logging.getLogger(__name__).error(
            f"Status Code: {response.status_code} | Failed to get NWS weather data for zip code: {zip_code}"
        )
        return None

    try:
        nws_weather_data = NWSWeatherData(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).error(
            f"Error: ValidationError | Failed to get NWS weather data for zip code: {zip_code}\n{e}"
        )
        return None

    current_top_of_hour_utc_time = arrow.utcnow().floor("hour")
    current_hourly_period = next(
        (
            hourly_period
            for hourly_period in nws_weather_data.properties.periods
            if arrow.get(hourly_period.start_time).to("UTC")
            == current_top_of_hour_utc_time
        ),
        None,
    )
    if not current_hourly_period:
        logging.getLogger(__name__).error(
            f"Failed to get NWS weather data for the current hourly period for zip code: {zip_code}"
        )
        return None

    sanitized_weather_data = SanitizedWeatherData(
        date_time=arrow.get(current_hourly_period.start_time).to("UTC"),
        temperature=current_hourly_period.temperature,
        rain_probability=current_hourly_period.rain_probability.value,
    )
    return sanitized_weather_data


if __name__ == "__main__":
    with open("test_data/forecast_hourly_response.json", "r") as f:
        import json

        test_data = NWSWeatherData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(
            test_data.properties.periods[1].start_time,
            type(test_data.properties.periods[1].start_time),
        )
        print(
            test_data.properties.periods[1].end_time,
            type(test_data.properties.periods[1].end_time),
        )
        print(
            test_data.properties.periods[1].temperature,
            type(test_data.properties.periods[1].temperature),
        )
        print(
            test_data.properties.periods[1].rain_probability.value,
            type(test_data.properties.periods[1].rain_probability.value),
        )

        print("")
        test_start_time = "2025-11-17T16:00:00-05:00"
        test_current_top_of_hour_utc_time = arrow.get(test_start_time).to("UTC")
        test_current_hourly_period = next(
            (
                hourly_period
                for hourly_period in test_data.properties.periods
                if arrow.get(hourly_period.start_time).to("UTC")
                == test_current_top_of_hour_utc_time
            ),
            None,
        )

        test_sanitized_weather_data = SanitizedWeatherData(
            date_time=arrow.get(test_current_hourly_period.start_time).to("UTC"),
            temperature=test_current_hourly_period.temperature,
            rain_probability=test_current_hourly_period.rain_probability.value,
        )
        print(
            test_sanitized_weather_data.date_time,
            type(test_sanitized_weather_data.date_time),
        )
        print(
            test_sanitized_weather_data.temperature,
            type(test_sanitized_weather_data.temperature),
        )
        print(
            test_sanitized_weather_data.rain_probability,
            type(test_sanitized_weather_data.rain_probability),
        )
