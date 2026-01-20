import asyncio
import math
from typing import Optional

from pydantic import BaseModel

from app.services.external.weather_apis.nws.weather_data import NWSAPI
from app.services.external.weather_apis.open_meteo.weather_data import OpenMeteoAPI
from app.services.external.weather_apis.weather_interface import (
    IWeatherGetter,
    NormalizedWeatherData,
)
from app.services.external.weather_apis.weatherapi.weather_data import WeatherAPI

__WEATHER_GETTERS: list[IWeatherGetter] = [
    OpenMeteoAPI(),
    NWSAPI(),
    WeatherAPI(),
]


# TODO: Maybe use a dataclass here?
class AggregateWeatherData(BaseModel):
    avg_temp: int
    avg_rain_prob: int


# TODO: Decide if date_time will be kept for the user here
async def get_aggregated_weather_data(zip_code: str) -> Optional[AggregateWeatherData]:
    # # Date/time format: Arrow object in UTC time ("YYYY-MM-DDTHH:mm:ss+00:00")
    # date_time: arrow.arrow.Arrow = arrow.get(
    #     arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
    # ).to("UTC")

    tasks = []
    for w in __WEATHER_GETTERS:
        tasks.append(w.get_weather_data(zip_code))

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
    aggregated_weather_data = AggregateWeatherData(
        avg_temp=avg_temp, avg_rain_prob=avg_rain_prob
    )
    return aggregated_weather_data


if __name__ == "__main__":
    import random

    class TestWeatherGetter(IWeatherGetter):
        @staticmethod
        async def get_weather_data(zip_code: str) -> Optional[NormalizedWeatherData]:
            if zip_code != "foo":
                return None

            temperature = random.uniform(0.0, 90.0)
            rain_probability = random.randint(0, 100)
            return NormalizedWeatherData(temperature, rain_probability)

    __WEATHER_GETTERS: list[IWeatherGetter] = [
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
        TestWeatherGetter(),
    ]

    result = asyncio.run(get_aggregated_weather_data("foo"))
    print(result)
    print("DONE")
