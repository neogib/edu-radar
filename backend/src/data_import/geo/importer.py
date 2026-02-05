import csv
import logging
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import cast

from geoalchemy2 import WKBElement
from geoalchemy2.shape import (
    from_shape,  # pyright: ignore[reportUnknownVariableType]
    to_shape,
)
from shapely.geometry import Point

from src.app.models.schools import Szkola
from src.data_import.api.exceptions import APIRequestError
from src.data_import.config.core import CSV_DIR
from src.data_import.config.geo import GeocodingSettings
from src.data_import.geo.exceptions import GeocodingError
from src.data_import.utils.api_request import api_request
from src.data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class ProcessingStats(Enum):
    PROCESSED = "processed"
    COORDINATES_IN_BUILDING = "coordinates_in_building"
    FAILED_GEOCODING = "failed_geocoding"
    SUCCESSFUL_GEOCODING = "successful_geocoding"


class SchoolCoordinatesImporter(DatabaseManagerBase):
    def __init__(
        self,
        converted_file: str | Path = CSV_DIR / "converted_addresses.csv",
    ):
        super().__init__()
        self.converted_file: str | Path = converted_file
        self.stats: dict[str, int] = defaultdict(int)

    def update_school_coordinates(self) -> None:
        """
        Updates school geolocation data based on the CSV file.
        """
        session = self._ensure_session()

        # Define required columns
        col_id = "id"
        col_lon = "g_dlug"
        col_lat = "g_szer"
        try:
            with open(self.converted_file, encoding="utf-8") as csvfile:
                # Use DictReader to automatically handle headers
                reader = csv.DictReader(csvfile)

                # Validate headers exist
                if not reader.fieldnames or not {col_id, col_lat, col_lon}.issubset(
                    reader.fieldnames
                ):
                    logger.critical(
                        f"🚨 Critical error: Missing required headers in CSV. Expected: {col_id}, {col_lat}, {col_lon}"
                    )
                    return

                for row in reader:
                    logger.debug(f"Processing row: {row}")

                    # validate data presence
                    raw_id = row.get(col_id, "").strip()
                    raw_lon = row.get(col_lon, "").strip()
                    raw_lat = row.get(col_lat, "").strip()

                    if not raw_id:
                        logger.error("Missing school ID in row, skipping.")
                        continue

                    # find school
                    school_id = int(raw_id)
                    school = session.get(Szkola, school_id)

                    if not school:
                        logger.warning(f"School with ID {school_id} not found.")
                        continue

                    if not raw_lon or not raw_lat:
                        # Check if current coordinates are valid (in a building)
                        if self.is_point_in_building(school):
                            self.stats[
                                ProcessingStats.COORDINATES_IN_BUILDING.value
                            ] += 1
                            continue

                        new_data = self.investigate_missing_data(school)

                        if new_data is None:  # there was an error during geocoding
                            self.stats[ProcessingStats.FAILED_GEOCODING.value] += 1
                            continue

                        lon, lat = new_data
                        logger.info(
                            f"Updated missing data for school ID {school_id}: Lat={lon}, Lon={lat}"
                        )
                    else:  # normal case - coordinates are present
                        try:
                            lon = float(raw_lon)
                            lat = float(raw_lat)
                        except ValueError:
                            logger.error(
                                f"Invalid coordinate format for ID {school_id}"
                            )
                            continue

                    school.geom = from_shape(Point(lon, lat), srid=4326)
                    session.add(school)
                    self.stats[ProcessingStats.PROCESSED.value] += 1

                    # Commit every 100 records to avoid large transactions
                    if self.stats[ProcessingStats.PROCESSED.value] % 100 == 0:
                        session.commit()

                # Final commit for remaining records
                session.commit()
                for stats in ProcessingStats:
                    logger.info(f"Stat - {stats.value}: {self.stats[stats.value]}")

        except FileNotFoundError:
            logger.critical(f"File not found: {self.converted_file}")
        except Exception as e:
            session.rollback()
            logger.critical(f"Unexpected error during import: {e}")
            raise

    def investigate_missing_data(self, school: Szkola) -> None | tuple[float, float]:
        try:
            logger.info(
                f"🔍 Invalid coordinates for school {school.nazwa} (ID: {school.id}). Geocoding..."
            )

            # Prepare address components
            city = school.miejscowosc.nazwa

            # Normalize city name for geocoding - for the biggest cities miejscowosc is actually district and we need to change that
            if city in GeocodingSettings.WARSAW_DISTRICTS:
                city = "Warszawa"
            # Check for other big cities, districts starts with "CityName-", for example "Wrocław-Psie Pole"
            for big_city in GeocodingSettings.POLAND_BIGGEST_CITIES:
                if city.startswith(f"{big_city}-"):
                    city = big_city
                    break
            street = school.ulica.nazwa if school.ulica else None
            building_number = school.numer_budynku

            # Geocode address
            return self.geocode_address(city, street, building_number)

        except GeocodingError as e:
            logger.error(
                f"⚠️ Failed to geocode school {school.nazwa} (ID: {school.id}): {e}"
            )
        except Exception as e:
            logger.error(
                f"💥 Unexpected error processing school {school.nazwa} (ID: {school.id}): {e}"
            )

    def geocode_address(
        self,
        city: str,
        street: str | None = None,
        building_number: str | None = None,
    ) -> tuple[float, float] | None:
        """
        Geocode an address using the UUG service.

        Args:
            city: City name
            street: Street name (optional)
            building_number: Building number (optional)

        Raises:
            GeocodingError: If geocoding request fails
        """
        # Build request query string
        full_address = city

        if street:
            full_address += f", {street}"

        if building_number:
            full_address += f" {building_number}"

        params: dict[str, object] = {
            "request": "GetAddress",
            "address": full_address,
            "srid": GeocodingSettings.SRID_WGS84,
        }

        try:
            data = cast(
                dict[str, object],
                api_request(url=GeocodingSettings.UUG_URL, params=params),
            )
            result = self._extract_lat_lon_from_uug(data)
        except APIRequestError as err:
            logger.error(f"❌ Geocoding failed for: {full_address}: {err}")
            raise GeocodingError(
                "Failed to geocode address",
                address=full_address,
            ) from err
        if result:
            self.stats[ProcessingStats.SUCCESSFUL_GEOCODING.value] += 1
        return result

    def is_point_in_building(self, school: Szkola) -> bool:
        """
        Get building information from coordinates using ULDK service.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Raises:
            GeocodingError: If building lookup fails

        Returns:
            bool: True if point is within a building, False otherwise
        """
        # Extract current coordinates from geom
        point = cast(Point, to_shape(cast(WKBElement, school.geom)))
        lon, lat = point.x, point.y

        params: dict[str, object] = {
            "request": "GetBuildingByXY",
            "xy": f"{lon},{lat},{GeocodingSettings.SRID_WGS84}",
            "result": "id,function,parcel,region,commune,county,voivodeship,geom_wkt",
        }

        try:
            data = api_request(url=GeocodingSettings.ULDK_URL, params=params)
            return self._validate_uldk_response(data)
        except APIRequestError as err:
            coords = f"({lat}, {lon})"
            logger.error(f"❌ Building lookup failed for coords {coords}: {err}")
            raise GeocodingError(
                f"Failed to get building info for coordinates: {coords}",
                address=coords,
            ) from err

    def _extract_lat_lon_from_uug(
        self, data: dict[str, object]
    ) -> tuple[float, float] | None:
        """Parse the UUG API response to get latitude."""
        # UUG returns results in 'results' list
        results = cast(dict[str, object], data.get("results", {}))

        if not results:
            logger.warning("🚫 No results found in UUG response")
            return None

        first_result = cast(dict[str, object], results.get("1"))

        try:
            lon = float(cast(str, first_result.get("x")))
            lat = float(cast(str, first_result.get("y")))
        except (TypeError, ValueError) as _:
            logger.error("❌ Invalid coordinate values in UUG response")

            return None

        logger.info(f"🔄 Transformed coordinates: {lat}, {lon}")
        return lon, lat

    def _validate_uldk_response(self, data: object) -> bool:
        """Validate the ULDK API response for building presence."""
        # ULDK returns pipe-separated values or -1 for no results
        result_str = str(data)

        # edge case when uldk is not working
        if "nie zwróciła" in result_str:
            logger.warning("🚫 ULDK service did not return valid data")
            return True  # assume point is in building to avoid false negatives

        if result_str.startswith("-1"):  # no building found
            return False

        return True
