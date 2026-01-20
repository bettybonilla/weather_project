import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError

from app.services.external.weather_apis.location_api.geocoding.location_data import (
    get_location_data,
)
from app.services.external.weather_apis.weather_interface import (
    IWeatherGetter,
    NormalizedWeatherData,
)


class WeatherData(BaseModel):
    temperature: float = Field(alias="temperature_2m")

    # Percentage: 0-100
    rain_probability: int = Field(alias="precipitation_probability")


class OpenMeteoDataModel(BaseModel):
    latitude: float
    longitude: float
    current: WeatherData


# Based on 15 min interval
class OpenMeteoAPI(IWeatherGetter):
    @staticmethod
    def get_weather_data(zip_code: str) -> Optional[NormalizedWeatherData]:
        geocoding_location_data = get_location_data(zip_code)
        if geocoding_location_data is None:
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
            open_meteo = OpenMeteoDataModel(**response.json())
            normalized_weather_data = NormalizedWeatherData(
                temperature=open_meteo.current.temperature,
                rain_probability=open_meteo.current.rain_probability,
            )
        except ValidationError as e:
            logging.getLogger(__name__).error(
                f"Error: ValidationError | Failed to get Open-Meteo weather data for zip code: {zip_code}\n{e}"
            )
            return None
        return normalized_weather_data


if __name__ == "__main__":
    test_open_meteo = OpenMeteoAPI()
    test_data = test_open_meteo.get_weather_data("07310")
    print(test_data.temperature, type(test_data.temperature))
    print(test_data.rain_probability, type(test_data.rain_probability))
    print()

    with open("test_data/response.json", "r") as f:
        import json

        test_data = OpenMeteoDataModel(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.current.temperature, type(test_data.current.temperature))
        print(
            test_data.current.rain_probability, type(test_data.current.rain_probability)
        )
