# TODO: Use as global normalizer for all weather data
class WeatherData:
    # Should be a type of Date object
    # Date/time format: ISO 8601 ("YYYY-MM-DDTHH:mm")
    date_time: str
    temperature: float
    # Percentage: 0-100
    rain_probability: int


class NormalizedWeatherData:
    latitude: float
    longitude: float
    current: WeatherData
