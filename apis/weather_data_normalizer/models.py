import arrow


# Date/time format: Arrow object in UTC time ("YYYY-MM-DDTHH:mm:ss+00:00")
date_time: arrow.arrow.Arrow = arrow.get(
    arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
).to("UTC")


# Based on current hour
class WeatherData:
    temperature: float
    # Percentage: 0-100
    rain_probability: int


class NormalizedWeatherData:
    latitude: float
    longitude: float
    current: WeatherData
