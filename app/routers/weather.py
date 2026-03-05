import logging

from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_db
from app.services.external.weather_apis.aggregator import (
    AggregatedWeatherData,
    get_aggregated_weather_data,
)


async def retriever_handler(
    r: Request, db: AsyncSession = Depends(get_db)
) -> AggregatedWeatherData | Response:
    requested_zip_code = r.query_params.get("zip_code")
    if requested_zip_code is None:
        logging.getLogger(__name__).error(
            f"Missing the required zip_code query parameter"
        )
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    aggregated_weather_data = await get_aggregated_weather_data(requested_zip_code, db)
    if aggregated_weather_data is None:
        logging.getLogger(__name__).error(
            f"Failed to get aggregated weather data for zip code: {requested_zip_code}"
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # FastAPI converts this Pydantic model to JSON
    return aggregated_weather_data
