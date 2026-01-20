import logging
from typing import Optional

import arrow
import requests
from pydantic import BaseModel, Field, ValidationError

from app.services.external.weather_apis.nws.points_url import get_points_url
from app.services.external.weather_apis.weather_interface import (
    IWeatherGetter,
    NormalizedWeatherData,
)


class Value(BaseModel):
    value: int


class Period(BaseModel):
    # Date/time format: ISO 8601 ("YYYY-MM-DDTHH:mm:ss±HH:mm")
    start_time: str = Field(alias="startTime")
    end_time: str = Field(alias="endTime")

    temperature: float

    # Percentage: 0-100
    rain_probability: Value = Field(alias="probabilityOfPrecipitation")


class Property(BaseModel):
    # List of hourly periods over the next seven days
    periods: list[Period]

    # Default value: "us"
    units: str


class NWSDataModel(BaseModel):
    properties: Property


# Based on current hour
class NWSAPI(IWeatherGetter):
    @staticmethod
    def get_weather_data(zip_code: str) -> Optional[NormalizedWeatherData]:
        nws_points_url = get_points_url(zip_code)
        if nws_points_url is None:
            logging.getLogger(__name__).error(
                f"Failed to get NWS points URL for zip code: {zip_code}"
            )
            return None

        redirect_url = nws_points_url.forecast_hourly_url
        if not redirect_url:
            logging.getLogger(__name__).error(
                f"Failed to get redirect URL for zip code: {zip_code}"
            )
            return None

        response = requests.get(
            redirect_url, headers={"Accept": "application/geo+json"}
        )
        if response.status_code != 200:
            logging.getLogger(__name__).error(
                f"Status Code: {response.status_code} | Failed to get NWS weather data for zip code: {zip_code}"
            )
            return None

        try:
            nws = NWSDataModel(**response.json())
        except ValidationError as e:
            logging.getLogger(__name__).error(
                f"Error: ValidationError | Failed to get NWS weather data for zip code: {zip_code}\n{e}"
            )
            return None

        current_top_of_hour_utc_time = arrow.utcnow().floor("hour")
        current_hourly_period = next(
            (
                hourly_period
                for hourly_period in nws.properties.periods
                if arrow.get(hourly_period.start_time).to("UTC")
                == current_top_of_hour_utc_time
            ),
            None,
        )

        if current_hourly_period is None:
            logging.getLogger(__name__).error(
                f"Failed to get NWS weather data for the current hourly period for zip code: {zip_code}"
            )
            return None

        normalized_weather_data = NormalizedWeatherData(
            temperature=current_hourly_period.temperature,
            rain_probability=current_hourly_period.rain_probability.value,
        )
        return normalized_weather_data


if __name__ == "__main__":
    test_nws = NWSAPI()
    test_data = test_nws.get_weather_data("07310")
    print(test_data.temperature, type(test_data.temperature))
    print(test_data.rain_probability, type(test_data.rain_probability))
    print()

    with open("test_data/forecast_hourly_url_response.json", "r") as f:
        import json

        test_data = NWSDataModel(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(
            test_data.properties.periods[1].temperature,
            type(test_data.properties.periods[1].temperature),
        )
        print(
            test_data.properties.periods[1].rain_probability.value,
            type(test_data.properties.periods[1].rain_probability.value),
        )

        print()
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

        test_normalized_weather_data = NormalizedWeatherData(
            temperature=test_current_hourly_period.temperature,
            rain_probability=test_current_hourly_period.rain_probability.value,
        )
        print(
            test_normalized_weather_data.temperature,
            type(test_normalized_weather_data.temperature),
        )
        print(
            test_normalized_weather_data.rain_probability,
            type(test_normalized_weather_data.rain_probability),
        )
