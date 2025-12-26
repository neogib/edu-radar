import logging
from typing import cast

from pyproj import Transformer
from sqlmodel import select

from src.app.models.schools import Szkola
from src.data_import.api.exceptions import APIRequestError
from src.data_import.api.types import SimpleDict
from src.data_import.core.config import GeocodingSettings
from src.data_import.geo.exceptions import GeocodingError
from src.data_import.utils.db.session import DatabaseManagerBase
from src.data_import.utils.requests import api_request

logger = logging.getLogger(__name__)


class GeoCoder(DatabaseManagerBase):
    """
    Geocode addresses using Polish GUGiK services.

    Iterates over schools in the database, verifies their coordinates against building locations,
    and updates incorrect coordinates by geocoding the address.
    """

    def __init__(
        self,
        uug_url: str = GeocodingSettings.UUG_URL,
        uldk_url: str = GeocodingSettings.ULDK_URL,
    ):
        super().__init__()
        self.uug_url: str = uug_url
        self.uldk_url: str = uldk_url

    def update_school_coordinates(self, batch_size: int = 1000) -> None:
        """
        Iterate over all schools, validate coordinates, and update if necessary.

        Args:
            batch_size: Number of schools to fetch and process at a time
        """
        session = self._ensure_session()
        offset = 0
        total_processed = 0

        while True:
            # Fetch schools in batches
            schools = session.exec(
                select(Szkola).offset(offset).limit(batch_size)
            ).all()

            if not schools:
                break  # No more schools to process

            logger.info(
                f"⏳ Processing batch {offset // batch_size + 1}: {len(schools)} schools"
            )

            for school in schools:
                try:
                    # Check if current coordinates are valid (in a building)
                    is_valid = self.is_point_in_building(
                        school.geolokalizacja_latitude, school.geolokalizacja_longitude
                    )

                    if is_valid:
                        logger.info(
                            f"✅ Skipping school {school.nazwa} (ID: {school.id}) - coordinates valid."
                        )
                        continue

                    logger.info(
                        f"🔍 Invalid coordinates for school {school.nazwa} (ID: {school.id}). Geocoding..."
                    )
                    logger.info(
                        f"Validating coordinates... {school.geolokalizacja_latitude}, {school.geolokalizacja_longitude}"
                    )

                    # Prepare address components
                    city = school.miejscowosc.nazwa
                    street = school.ulica.nazwa if school.ulica else None
                    building_number = school.numer_budynku

                    # Geocode address
                    new_coords = self.geocode_address(city, street, building_number)

                    # Update school
                    school.geolokalizacja_latitude = new_coords[0]
                    school.geolokalizacja_longitude = new_coords[1]

                    session.add(school)
                    session.commit()

                    logger.info(
                        f"📍 Updated coordinates for school {school.nazwa} (ID: {school.id})."
                    )
                    total_processed += 1

                except GeocodingError as e:
                    logger.error(
                        f"⚠️ Failed to geocode school {school.nazwa} (ID: {school.id}): {e}"
                    )
                except Exception as e:
                    logger.error(
                        f"💥 Unexpected error processing school {school.nazwa} (ID: {school.id}): {e}"
                    )

            # Move to next batch
            offset += batch_size

        logger.info(
            f"✅ Completed coordinate validation. Total schools processed: {total_processed}"
        )

    def geocode_address(
        self,
        city: str,
        street: str | None = None,
        building_number: str | None = None,
    ) -> tuple[float, float]:
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

        params: dict[str, str] = {
            "request": "GetAddress",
            "address": full_address,
        }

        try:
            data = api_request(url=self.uug_url, params=params)
            result = self._extract_lat_lon_from_uug(data)
        except APIRequestError as err:
            logger.error(f"❌ Geocoding failed for: {full_address}: {err}")
            raise GeocodingError(
                "Failed to geocode address",
                address=full_address,
            ) from err
        if result is None:
            raise GeocodingError(
                "No geocoding results found",
                address=full_address,
            )
        return result

    def is_point_in_building(self, latitude: float, longitude: float) -> bool:
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
        params = {
            "request": "GetBuildingByXY",
            "xy": f"{longitude},{latitude},{GeocodingSettings.SRID_WGS84}",
            "result": "id,function,parcel,region,commune,county,voivodeship,geom_wkt",
        }

        try:
            data = api_request(url=self.uldk_url, params=params)
            return self._validate_uldk_response(data)
        except APIRequestError as err:
            coords = f"({latitude}, {longitude})"
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

        first_result = cast(SimpleDict, results.get("1"))
        transformer = Transformer.from_crs(
            GeocodingSettings.SRID_POL,  # PUWG 1992
            GeocodingSettings.SRID_WGS84,  # WGS84 (lon, lat)
            always_xy=True,
        )
        try:
            x, y = float(first_result.get("x")), float(first_result.get("y"))
        except (TypeError, ValueError) as _:
            logger.error("❌ Invalid coordinate values in UUG response")

            return None
        lon, lat = cast(
            tuple[float, float],
            transformer.transform(x, y),
        )
        logger.info(f"🔄 Transformed coordinates: {lat}, {lon}")
        return lat, lon

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
