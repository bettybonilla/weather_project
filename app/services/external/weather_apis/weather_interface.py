from typing import Protocol, Optional


class NormalizedWeatherData:
    def __init__(self, temperature: float, rain_probability: int):
        self.temperature: float = temperature

        # Percentage: 0-100
        self.rain_probability: int = rain_probability


class IWeatherGetter(Protocol):
    @staticmethod
    def get_weather_data(zip_code: str) -> Optional[NormalizedWeatherData]:
        pass
