import logging

from app.services.external.weather_apis.aggregator import get_aggregated_weather_data


async def retriever_handler(zip_code: str):
    aggregated_weather_data = await get_aggregated_weather_data(zip_code)
    if aggregated_weather_data is None:
        logging.getLogger(__name__).error(
            f"Failed to get aggregated weather data for zip code: {zip_code}"
        )
        return None

    # FastAPI converts this Pydantic model to JSON
    return aggregated_weather_data
