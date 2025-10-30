import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field, ValidationError

_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"


class Result(BaseModel):
    country: str
    country_code: str
    state: str = Field(alias="admin1")
    city: str = Field(alias="name")
    # These zip codes share the same lat, long results
    postcodes: list[str]
    latitude: float
    longitude: float
    timezone: str


class GeocodingData(BaseModel):
    results: list[Result]


def get_location_data(zip_code: str) -> Optional[Result]:
    response = requests.get(
        _BASE_URL, headers={"Accept": "application/json"}, params={"name": zip_code}
    )
    if response.status_code != 200:
        logging.getLogger(__name__).warning(
            f"Status Code: {response.status_code} | Failed to get location data for zip code: {zip_code}"
        )
        return None

    try:
        geocoding_data = GeocodingData(**response.json())
    except ValidationError:
        logging.getLogger(__name__).warning(
            f"Error: ValidationError | Failed to get location data for zip code: {zip_code}"
        )
        return None

    for result in geocoding_data.results:
        if result.country_code == "US":
            return result
    logging.getLogger(__name__).warning(
        f"Failed to get location data in the US for zip code: {zip_code}"
    )
    return None


if __name__ == "__main__":
    with open("test_data/response.json", "r") as f:
        import json

        test_data = GeocodingData(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.results[0])
        print(test_data.results[0].state)
        print(test_data.results[0].city)
    print("-----------------------")
    location_data = get_location_data(zip_code="07310")
    print(location_data)
    print(location_data.latitude)
    print(location_data.longitude)
