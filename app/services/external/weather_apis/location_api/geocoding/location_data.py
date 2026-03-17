import logging
from typing import Optional

import arrow
import requests_async as requests
from fastapi import Depends
from pydantic import BaseModel
from pydantic import Field, ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import REQUEST_TIMEOUT
from app.database import get_db
from app.models.zip_code import ZipCode


class GeocodingResult(BaseModel):
    # These zip codes share the same lat, long results
    zip_codes: list[str] = Field(alias="postcodes")

    country: str
    country_code: str
    state: str = Field(alias="admin1")
    city: str = Field(alias="name")
    latitude: float
    longitude: float
    timezone: str

    def to_location_data_result(self, requested_zip_code: str) -> Result:
        location_data_result = Result(
            zip_code=requested_zip_code,
            latitude=self.latitude,
            longitude=self.longitude,
            country_code=self.country_code,
            state=self.state,
            city=self.city,
        )
        return location_data_result


class GeocodingDataModel(BaseModel):
    results: list[GeocodingResult]


class Result:
    def __init__(
        self,
        zip_code: str,
        latitude: float,
        longitude: float,
        country_code: str,
        state: str,
        city: str,
    ):
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude
        self.country_code = country_code
        self.state = state
        self.city = city

    def get_zip_code(self) -> str:
        return self.zip_code

    def get_lat_long(self) -> tuple[float, float]:
        return self.latitude, self.longitude


async def get_location_data(
    requested_zip_code: str, db: AsyncSession = Depends(get_db)
) -> Optional[Result | GeocodingResult]:
    # DB lookup
    async with db.begin():
        stmt = select(ZipCode).where(ZipCode.zip_code == requested_zip_code)
        result = await db.execute(stmt)
        db_row: Optional[ZipCode] = result.scalar_one_or_none()

    # Fast path: Found in DB -> Build Result from DB
    if db_row:
        location_data_result = Result(
            zip_code=requested_zip_code,
            latitude=db_row.latitude,
            longitude=db_row.longitude,
            country_code=db_row.country_code,
            state=db_row.state,
            city=db_row.city,
        )
        return location_data_result

    # Slow path: Not found in DB -> Build Result after API call and upsert into DB
    base_url = "https://geocoding-api.open-meteo.com/v1/search"

    try:
        response = await requests.get(
            url=base_url,
            headers={"Accept": "application/json"},
            params={"name": requested_zip_code},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            logging.getLogger(__name__).warning(
                f"Status Code: {response.status_code} | Failed to get Geocoding location data for zip code: {requested_zip_code}"
            )
            return None
    except Exception as e:
        logging.getLogger(__name__).warning(
            f"Error: Exception | Failed to get Geocoding location data for zip code: {requested_zip_code} | {e}"
        )
        return None

    try:
        geocoding = GeocodingDataModel(**response.json())
    except ValidationError as e:
        logging.getLogger(__name__).warning(
            f"Error: ValidationError | Failed to get Geocoding location data for zip code: {requested_zip_code} | {e}"
        )
        return None

    us_result = next(
        (result for result in geocoding.results if result.country_code == "US"),
        None,
    )

    if us_result is None:
        logging.getLogger(__name__).warning(
            f"Failed to get Geocoding location data in the US for zip code: {requested_zip_code}"
        )
        return None

    # Choosing to manually use raw SQL for practice instead of using SQLAlchemy ORM features
    try:
        # Transactional upsert
        # Commits transaction at the end or rolls back if the exception is raised
        async with db.begin():
            for zc in us_result.zip_codes:
                # Example of how to use the SQLAlchemy ORM features
                # Known bug at db.merge() therefore it does not upsert into DB
                # z = ZipCode(
                #     zip_code=zc,
                #     latitude=us_result.latitude,
                #     longitude=us_result.longitude,
                #     country_code=us_result.country_code,
                #     state=us_result.state,
                #     city=us_result.city,
                # )
                # db.merge(z)

                # Raw SQL is king - Full control, no magic involved
                tx = text(
                    """
                    INSERT INTO zip_codes (zip_code, latitude, longitude, country_code, state, city)
                    VALUES (:zip_code, :latitude, :longitude, :country_code, :state, :city)
                    ON DUPLICATE KEY UPDATE
                        updated_at = :updated_at;
                    """
                )
                await db.execute(
                    tx,
                    {
                        "zip_code": zc,
                        "latitude": us_result.latitude,
                        "longitude": us_result.longitude,
                        "country_code": us_result.country_code,
                        "state": us_result.state,
                        "city": us_result.city,
                        "updated_at": arrow.utcnow(),
                    },
                )
    except SQLAlchemyError as e:
        logging.getLogger(__name__).error(
            f"Error: SQLAlchemyError | Failed to upsert into the zip_codes database table | {e}"
        )
        return us_result

    return us_result.to_location_data_result(requested_zip_code)


if __name__ == "__main__":
    with open("test_data/response.json", "r") as f:
        import json

        test_data = GeocodingDataModel(**json.load(f))
        # print(test_data.model_dump_json(indent=4))
        print(test_data.results[0])
        print(test_data.results[0].state, type(test_data.results[0].state))
        print(test_data.results[0].city, type(test_data.results[0].city))
        print(test_data.results[0].zip_codes, type(test_data.results[0].zip_codes))
        print(test_data.results[0].latitude, type(test_data.results[0].latitude))
        print(test_data.results[0].longitude, type(test_data.results[0].longitude))

        print()
        test_data.results[0].to_location_data_result(
            test_data.results[0].zip_codes[0]
        ).get_lat_long()
        print(
            type(
                test_data.results[0]
                .to_location_data_result(test_data.results[0].zip_codes[0])
                .get_lat_long()
            ),
        )
