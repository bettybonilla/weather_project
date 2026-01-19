import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError

import apis.geocoding.location_data


class Property(BaseModel):
    forecast_hourly: str = Field(alias="forecastHourly")
    grid_id: str = Field(alias="gridId")
    grid_x: int = Field(alias="gridX")
    grid_y: int = Field(alias="gridY")


class NWSPointsData(BaseModel):
    properties: Property


def _get_points_data(zip_code: str) -> Optional[Property]:
    geocoding_location_data = apis.geocoding.location_data.get_location_data(zip_code)
    if not geocoding_location_data:
        logging.getLogger(__name__).warning(
            f"Failed to get geocoding location data for zip code: {zip_code}"
        )
        return None

    lat, long = geocoding_location_data.get_lat_long()
    base_url = "https://api.weather.gov/points"
    response = requests.get(
        f"{base_url}/{lat},{long}", headers={"Accept": "application/geo+json"}
    )
    if response.status_code != 200:
        logging.getLogger(__name__).warning(
            f"Status Code: {response.status_code} | Failed to get NWS points data for zip code: {zip_code}"
        )
        return None

    try:
        nws_points_data = NWSPointsData(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).warning(
            f"Error: ValidationError | Failed to get NWS points data for zip code: {zip_code}\n{e}"
        )
        return None
    return nws_points_data.properties


# TODO: Move to test file
if __name__ == "__main__":
    with open("test_data/points_data_response.json", "r") as f:
        import json

        test_data = NWSPointsData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(
            test_data.properties.forecast_hourly,
            type(test_data.properties.forecast_hourly),
        )
        print(test_data.properties.grid_id, type(test_data.properties.grid_id))
        print(test_data.properties.grid_x, type(test_data.properties.grid_x))
        print(test_data.properties.grid_y, type(test_data.properties.grid_y))
