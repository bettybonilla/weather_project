import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError

from app.config import REQUEST_TIMEOUT
from app.services.external.weather_apis.location_api.geocoding import location_data


class Property(BaseModel):
    forecast_hourly_url: str = Field(alias="forecastHourly")
    grid_id: str = Field(alias="gridId")
    grid_x: int = Field(alias="gridX")
    grid_y: int = Field(alias="gridY")


class NWSPointsURLDataModel(BaseModel):
    properties: Property


def get_points_url(
    location_data_result: Optional[location_data.Result],
) -> Optional[Property]:
    lat, long = location_data_result.get_lat_long()
    base_url = "https://api.weather.gov/points"
    response = requests.get(
        f"{base_url}/{lat},{long}",
        headers={"Accept": "application/geo+json"},
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code != 200:
        logging.getLogger(__name__).warning(
            f"Status Code: {response.status_code} | Failed to get NWS points URL for zip code: {location_data_result.get_zip_code()}"
        )
        return None

    try:
        nws_points_url = NWSPointsURLDataModel(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).warning(
            f"Error: ValidationError | Failed to get NWS points URL for zip code: {location_data_result.get_zip_code()}\n{e}"
        )
        return None
    return nws_points_url.properties


if __name__ == "__main__":
    with open("test_data/points_url_response.json", "r") as f:
        import json

        test_data = NWSPointsURLDataModel(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(
            test_data.properties.forecast_hourly_url,
            type(test_data.properties.forecast_hourly_url),
        )
        print(test_data.properties.grid_id, type(test_data.properties.grid_id))
        print(test_data.properties.grid_x, type(test_data.properties.grid_x))
        print(test_data.properties.grid_y, type(test_data.properties.grid_y))
