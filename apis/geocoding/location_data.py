import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError


class Result(BaseModel):
    country: str
    country_code: str
    state: str = Field(alias="admin1")
    city: str = Field(alias="name")
    # These zip codes share the same lat, long results
    zip_codes: list[str] = Field(alias="postcodes")
    latitude: float
    longitude: float
    timezone: str

    def get_lat_long(self) -> tuple[float, float]:
        return self.latitude, self.longitude


class GeocodingLocationData(BaseModel):
    results: list[Result]


def get_location_data(zip_code: str) -> Optional[Result]:
    base_url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(
        base_url, headers={"Accept": "application/json"}, params={"name": zip_code}
    )
    if response.status_code != 200:
        logging.getLogger(__name__).warning(
            f"Status Code: {response.status_code} | Failed to get geocoding location data for zip code: {zip_code}"
        )
        return None

    try:
        geocoding_location_data = GeocodingLocationData(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).warning(
            f"Error: ValidationError | Failed to get geocoding location data for zip code: {zip_code}\n{e}"
        )
        return None

    us_result = next(
        (
            result
            for result in geocoding_location_data.results
            if result.country_code == "US"
        ),
        None,
    )
    if not us_result:
        logging.getLogger(__name__).warning(
            f"Failed to get geocoding location data in the US for zip code: {zip_code}"
        )
        return None
    return us_result


if __name__ == "__main__":
    with open("test_data/response.json", "r") as f:
        import json

        test_data = GeocodingLocationData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.results[0])
        print(test_data.results[0].state, type(test_data.results[0].state))
        print(test_data.results[0].city, type(test_data.results[0].city))
        print(test_data.results[0].zip_codes, type(test_data.results[0].zip_codes))
        print(test_data.results[0].latitude, type(test_data.results[0].latitude))
        print(test_data.results[0].longitude, type(test_data.results[0].longitude))

        print("")
        print(
            test_data.results[0].get_lat_long(),
            type(test_data.results[0].get_lat_long()),
        )
