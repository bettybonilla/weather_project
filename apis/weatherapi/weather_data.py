import logging
import os
import xml.etree.ElementTree as ET
from typing import Optional

import arrow
import requests
from pydantic import ValidationError


# Based on 15 min interval
class WeatherAPIWeatherData:
    def __init__(self, response_xml: str):
        root = ET.fromstring(response_xml)
        child_current = root.find("current")
        child_location = root.find("location")

        # Date/time format: ISO 8601 ("YYYY-MM-DD HH:mm")
        original_date_time = child_current.find("last_updated").text

        tz_id = child_location.find("tz_id").text

        # Date/time format: Arrow object in UTC time ("YYYY-MM-DDTHH:mm:ss+00:00")
        self.date_time: arrow.arrow.Arrow = arrow.get(
            original_date_time, tzinfo=tz_id
        ).to("UTC")

        self.temperature: float = float(child_current.find("temp_f").text)

        # Normalizing rain_probability (precip_mm: int is in millimeters, not percentage)
        # Assumes 100% if precip_mm > 0
        precip_mm: int = int(child_current.find("precip_mm").text)
        self.rain_probability: int = 0
        if precip_mm > 0:
            self.rain_probability: int = 100


def get_weather_data(zip_code: str) -> Optional[WeatherAPIWeatherData]:
    api_key = os.getenv("WEATHERAPI_API_KEY")
    if not api_key:
        logging.getLogger(__name__).error("WEATHERAPI_API_KEY not found in environment")
        return None

    base_url = "https://api.weatherapi.com/v1/current.xml"
    response = requests.get(base_url, params={"key": api_key, "q": zip_code})
    if response.status_code != 200:
        logging.getLogger(__name__).error(
            f"Status Code: {response.status_code} | Failed to get WeatherAPI weather data for zip code: {zip_code}"
        )
        return None

    try:
        weatherapi_weather_data = WeatherAPIWeatherData(response.text)
    except ValidationError as e:
        logging.getLogger(__name__).error(
            f"Error: ValidationError | Failed to get WeatherAPI weather data for zip code: {zip_code}\n{e}"
        )
        return None
    return weatherapi_weather_data


# TODO: Move to test file
if __name__ == "__main__":
    with open("test_data/response.xml", "r") as f:
        emulated_response_xml = f.read()

        test_root = ET.fromstring(emulated_response_xml)
        test_child_current = test_root.find("current")
        print(
            test_child_current.find("last_updated").text,
            type(test_child_current.find("last_updated").text),
        )
        print(
            test_child_current.find("temp_f").text,
            type(test_child_current.find("temp_f").text),
        )
        print(
            test_child_current.find("precip_mm").text,
            type(test_child_current.find("precip_mm").text),
        )

        print()
        test_data = WeatherAPIWeatherData(emulated_response_xml)
        print(test_data.date_time, type(test_data.date_time))
        print(test_data.temperature, type(test_data.temperature))
        print(test_data.rain_probability, type(test_data.rain_probability))
