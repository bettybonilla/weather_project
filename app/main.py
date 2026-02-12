import logging
import sys

from fastapi import FastAPI, APIRouter, status

from app.routers import health
from app.routers import weather

# Configures the global root logger format
# The StreamHandler class sends the logs to the console
# stdout is typically white (OS contingent)
# stderr is typically red (OS contingent) -> stream parameter default
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format="%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s",
)

app = FastAPI()

# ROUTES ---------------------------------------------------------------------------------------------------------------

base = APIRouter()
base.get("/", status_code=status.HTTP_200_OK)(health.check_handler)
base.get("/health-check", status_code=status.HTTP_200_OK)(health.check_handler)
base.get("/weather-retriever", status_code=status.HTTP_200_OK)(
    weather.retriever_handler
)

app.include_router(base)

# ROUTES ---------------------------------------------------------------------------------------------------------------
