import logging
import os
import xml.etree.ElementTree as ET
from typing import Optional

import requests
from pydantic import ValidationError

from app.services.external.weather_apis.weather_interface import (
    IWeatherGetter,
    NormalizedWeatherData,
)


class WeatherAPIDataModel:
    def __init__(self, response_xml: str):
        root = ET.fromstring(response_xml)
        child_current = root.find("current")
        self.temperature: float = float(child_current.find("temp_f").text)

        # Normalizing rain_probability (precip_mm: int is in millimeters, not percentage)
        # Assumes 100% if precip_mm > 0
        precip_mm: int = int(child_current.find("precip_mm").text)
        self.rain_probability: int = 0
        if precip_mm > 0:
            self.rain_probability: int = 100


# Based on 15 min interval
class WeatherAPI(IWeatherGetter):
    @staticmethod
    def get_weather_data(zip_code: str) -> Optional[NormalizedWeatherData]:
        api_key = os.getenv("WEATHERAPI_API_KEY")
        if not api_key:
            logging.getLogger(__name__).error(
                "WEATHERAPI_API_KEY not found in environment"
            )
            return None

        base_url = "https://api.weatherapi.com/v1/current.xml"
        response = requests.get(base_url, params={"key": api_key, "q": zip_code})
        if response.status_code != 200:
            logging.getLogger(__name__).error(
                f"Status Code: {response.status_code} | Failed to get WeatherAPI weather data for zip code: {zip_code}"
            )
            return None

        try:
            weatherapi = WeatherAPIDataModel(response.text)
            normalized_weather_data = NormalizedWeatherData(
                temperature=weatherapi.temperature,
                rain_probability=weatherapi.rain_probability,
            )
        except ValidationError as e:
            logging.getLogger(__name__).error(
                f"Error: ValidationError | Failed to get WeatherAPI weather data for zip code: {zip_code}\n{e}"
            )
            return None
        return normalized_weather_data


if __name__ == "__main__":
    test_weatherapi = WeatherAPI()
    test_data = test_weatherapi.get_weather_data("07310")
    print(test_data.temperature, type(test_data.temperature))
    print(test_data.rain_probability, type(test_data.rain_probability))
    print()

    with open("test_data/response.xml", "r") as f:
        emulated_response_xml = f.read()
        test_data = WeatherAPIDataModel(emulated_response_xml)
        print(test_data.temperature, type(test_data.temperature))
        print(test_data.rain_probability, type(test_data.rain_probability))
