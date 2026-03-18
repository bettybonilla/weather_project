import logging
import sys

from fastapi import FastAPI, APIRouter, status

from app.routers import health
from app.routers import weather
from app.services.external.weather_apis.aggregator import AggregatedWeatherData

import coloredlogs

# fmt: Configures the global root logger format
# isatty: is a system function used to determine whether a given file descriptor is connected to a terminal (TTY) device.
coloredlogs.install(
    level=logging.DEBUG,
    logger=logging.getLogger(),
    fmt="%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s",
    stream=sys.stdout,
    isatty=True,  # force ANSI colors even in docker
)

app = FastAPI()

# ROUTES ---------------------------------------------------------------------------------------------------------------

base = APIRouter()
base.get("/", status_code=status.HTTP_200_OK)(health.check_handler)
base.get("/health-check", status_code=status.HTTP_200_OK)(health.check_handler)
base.get(
    "/weather-retriever",
    response_model=AggregatedWeatherData,
    status_code=status.HTTP_200_OK,
)(weather.retriever_handler)

app.include_router(base)

# ROUTES ---------------------------------------------------------------------------------------------------------------
