from typing import Protocol, Optional

from app.services.external.weather_apis.location_api.geocoding import location_data


class NormalizedWeatherData:
    def __init__(self, temperature: float, rain_probability: int):
        self.temperature: float = temperature

        # Percentage: 0-100
        self.rain_probability: int = rain_probability


class IWeatherGetter(Protocol):
    @staticmethod
    async def get_weather_data(
        location_data_result: Optional[location_data.Result],
    ) -> Optional[NormalizedWeatherData]:
        pass
