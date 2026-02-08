import csv
import logging
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import cast

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

from src.app.models.schools import Szkola
from src.data_import.api.exceptions import APIRequestError
from src.data_import.config.core import CSV_DIR
from src.data_import.config.geo import GeocodingSettings
from src.data_import.geo.exceptions import GeocodingError
from src.data_import.utils.api_request import api_request
from src.data_import.utils.db.session import DatabaseManagerBase
from src.data_import.utils.geo import (
    build_full_address,
    create_geom_point,
    normalize_city_name,
)

logger = logging.getLogger(__name__)


class ProcessingStats(Enum):
    PROCESSED = "processed"
    COORDINATES_IN_BUILDING = "coordinates_in_building"
    FAILED_GEOCODING = "failed_geocoding"
    SUCCESSFUL_GEOCODING = "successful_geocoding"


def _extract_lat_lon_from_uug(data: dict[str, object]) -> tuple[float, float] | None:
    """Parse UUG API response to get coordinates in (lon, lat) order."""
    results = cast(dict[str, object], data.get("results", {}))
    if not results:
        logger.warning("🚫 No results found in UUG response")
        return None

    first_result = cast(dict[str, object], results.get("1"))
    try:
        lon = float(cast(str, first_result.get("x")))
        lat = float(cast(str, first_result.get("y")))
    except (TypeError, ValueError):
        logger.error("❌ Invalid coordinate values in UUG response")
        return None

    logger.info(f"🔄 Transformed coordinates: {lat}, {lon}")
    return lon, lat


def _validate_uldk_response(data: object) -> bool:
    """Validate ULDK API response for building presence."""
    result_str = str(data)

    # Edge case when ULDK service is down - avoid false negatives.
    if "nie zwróciła" in result_str:
        logger.warning("🚫 ULDK service did not return valid data")
        return True

    if result_str.startswith("-1"):
        return False

    return True


class SchoolCoordinatesImporter(DatabaseManagerBase):
    def __init__(
        self,
        converted_file: str | Path = CSV_DIR / "converted_addresses.csv",
        starting_id: int | None = None,
    ):
        super().__init__()
        self.checkpoint_file: Path = GeocodingSettings.CHECKPOINT_FILE
        self.converted_file: str | Path = converted_file
        self.starting_id: int = (
            starting_id if starting_id is not None else self._load_checkpoint()
        )
        self.stats: dict[str, int] = defaultdict(int)

    def update_school_coordinates(self) -> None:
        """
        Updates school geolocation data based on the CSV file.
        Resumes from starting_id if set.
        """
        session = self._ensure_session()

        if self.starting_id:
            logger.info(f"🔄 Resuming import from ID: {self.starting_id}")

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

                    # Skip records until we reach starting_id
                    if self.starting_id and school_id < self.starting_id:
                        continue

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

                    school.geom = create_geom_point(lon, lat)
                    session.add(school)
                    self.stats[ProcessingStats.PROCESSED.value] += 1

                    # Commit every 100 records to avoid large transactions
                    if self.stats[ProcessingStats.PROCESSED.value] % 100 == 0:
                        session.commit()
                        self._save_checkpoint(school_id)

                # Final commit for remaining records
                session.commit()
                self._clear_checkpoint()
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
            city = normalize_city_name(school.miejscowosc.nazwa)
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
        full_address = build_full_address(city, street, building_number)

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
            result = _extract_lat_lon_from_uug(data)
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
            return _validate_uldk_response(data)
        except APIRequestError as err:
            coords = f"({lat}, {lon})"
            logger.error(f"❌ Building lookup failed for coords {coords}: {err}")
            raise GeocodingError(
                f"Failed to get building info for coordinates: {coords}",
                address=coords,
            ) from err

    def _load_checkpoint(self) -> int:
        """Load the last processed school ID from checkpoint file."""
        if self.checkpoint_file.exists():
            try:
                content = self.checkpoint_file.read_text().strip()
                if content:
                    return int(content)
            except (ValueError, OSError) as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return 0

    def _save_checkpoint(self, school_id: int) -> None:
        """Save the current school ID to checkpoint file."""
        try:
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoint_file.write_text(str(school_id))  # pyright: ignore[reportUnusedCallResult]
        except OSError as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def _clear_checkpoint(self) -> None:
        """Clear the checkpoint file after successful completion."""
        try:
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                logger.info("✅ Checkpoint cleared - import completed successfully")
        except OSError as e:
            logger.error(f"Failed to clear checkpoint: {e}")
