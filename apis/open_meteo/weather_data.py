from typing import Optional

import requests
from pydantic import BaseModel, Field

from apis.geocoding.lat_long import get_lat_long, get_location_data

_BASE_URL = "https://api.open-meteo.com/v1/forecast"


# Current weather data are based on 15 min interval
class WeatherData(BaseModel):
    date_time: str = Field(alias="time")
    temp: float = Field(alias="temperature_2m")
    rain_probability: int = Field(alias="precipitation_probability")


class OpenMeteoData(BaseModel):
    latitude: float
    longitude: float
    current: WeatherData


def get_weather_data(zip_code: str) -> Optional[OpenMeteoData]:
    lat_long = get_lat_long(zip_code, get_location_data)
    latitude = lat_long.get("latitude")
    longitude = lat_long.get("longitude")
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "current": [
            "temperature_2m",
            "precipitation_probability",
        ],
        "timezone": "auto",
    }
    response = requests.get(
        _BASE_URL, headers={"Accept": "application/json"}, params=params
    )
    if response.status_code != 200:
        return None
    open_meteo_data = OpenMeteoData(**response.json())
    return open_meteo_data


if __name__ == "__main__":
    with open("test_data/response.json", "r") as f:
        import json

        test_data = OpenMeteoData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.latitude)
        print(test_data.longitude)
        print(f"The date and time: {test_data.current.date_time}")
        print(f"The current temp: {test_data.current.temp}°F")
        print(f"The current rain probability: {test_data.current.rain_probability} %")
    print("-----------------------")
    weather_data = get_weather_data("07310")
    print(weather_data.latitude)
    print(weather_data.longitude)
    print(weather_data.current.date_time)
    print(weather_data.current.temp)
    print(weather_data.current.rain_probability)
