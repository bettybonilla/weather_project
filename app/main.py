import app.internal.logger  # configures colored logging on import
from fastapi import APIRouter, FastAPI, status
from app.routers import health, weather

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
