import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError

import apis.geocoding.location_data


# Based on 15 min interval (local time)
class WeatherData(BaseModel):
    # Date/time format: ISO 8601 ("YYYY-MM-DDTHH:mm")
    date_time: str = Field(alias="time")
    temperature: float = Field(alias="temperature_2m")
    # Percentage: 0-100
    rain_probability: int = Field(alias="precipitation_probability")


class OpenMeteoWeatherData(BaseModel):
    latitude: float
    longitude: float
    current: WeatherData


# TODO: Refactor to implement DRY principle
def get_weather_data(zip_code: str) -> Optional[WeatherData]:
    geocoding_location_data = apis.geocoding.location_data.get_location_data(zip_code)
    if not geocoding_location_data:
        logging.getLogger(__name__).error(
            f"Failed to get geocoding location data for zip code: {zip_code}"
        )
        return None
    lat, long = geocoding_location_data.get_lat_long()
    params = {
        "latitude": lat,
        "longitude": long,
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "current": [
            "temperature_2m",
            "precipitation_probability",
        ],
        "timezone": "auto",
    }
    base_url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(
        base_url, headers={"Accept": "application/json"}, params=params
    )
    if response.status_code != 200:
        logging.getLogger(__name__).error(
            f"Status Code: {response.status_code} | Failed to get Open-Meteo weather data for zip code: {zip_code}"
        )
        return None

    try:
        open_meteo_weather_data = OpenMeteoWeatherData(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).error(
            f"Error: ValidationError | Failed to get Open-Meteo weather data for zip code: {zip_code}\n{e}"
        )
        return None
    return open_meteo_weather_data.current


if __name__ == "__main__":
    with open("test_data/response.json", "r") as f:
        import json

        test_data = OpenMeteoWeatherData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.latitude)
        print(test_data.longitude)
        print(test_data.current.date_time)
        print(test_data.current.temperature)
        print(test_data.current.rain_probability)
