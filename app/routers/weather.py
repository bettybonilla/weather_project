import logging
from typing import Optional

from app.services.external.weather_apis.aggregator import get_aggregated_weather_data


async def retriever_handler(zip_code: str) -> Optional[str]:
    aggregated_weather_data = await get_aggregated_weather_data(zip_code)
    if aggregated_weather_data is None:
        logging.getLogger(__name__).error(
            f"Failed to get aggregated weather data for zip code: {zip_code}"
        )
        return None

    temperature = aggregated_weather_data.avg_temp
    rain_probability = aggregated_weather_data.avg_rain_prob
    return f"Based on the current hour for zip code: {zip_code}, the temperature is {temperature}°F with a rain probability of {rain_probability}%"
