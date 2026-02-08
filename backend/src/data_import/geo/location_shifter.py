import logging
import math

from sqlmodel import Numeric, cast, func, select, tuple_

from src.app.models.schools import Szkola
from src.data_import.config.geo import ShifterSettings
from src.data_import.utils.db.session import DatabaseManagerBase
from src.data_import.utils.geo import create_geom_point

logger = logging.getLogger(__name__)


def _group_schools_by_location(
    schools: list[tuple[Szkola, float, float]],
) -> dict[tuple[float, float], list[Szkola]]:
    location_groups: dict[tuple[float, float], list[Szkola]] = {}
    skipped_invalid = 0

    for school, lat, lon in schools:
        if lat == 0.0 or lon == 0.0:
            skipped_invalid += 1
            continue

        coords = (lat, lon)
        location_groups.setdefault(coords, []).append(school)

    if skipped_invalid > 0:
        logger.warning(
            f"⚠️ Skipped {skipped_invalid} schools with invalid coordinates (0.0)"
        )

    return location_groups


def _prepare_school_shifts(
    location_groups: dict[tuple[float, float], list[Szkola]],
    shift_value: float,
) -> list[tuple[Szkola, float, float]]:
    schools_to_shift: list[tuple[Szkola, float, float]] = []

    for coords, schools_at_location in location_groups.items():
        if len(schools_at_location) <= 1:
            continue

        base_lat, base_lon = coords
        for i, school in enumerate(schools_at_location[1:], start=1):
            new_lat, new_lon = _calculate_shifted_coordinates(
                base_lat=base_lat,
                base_lon=base_lon,
                index=i,
                shift_value=shift_value,
                points_per_circle=ShifterSettings.POINTS_PER_CIRCLE,
            )
            schools_to_shift.append((school, new_lat, new_lon))

    return schools_to_shift


def _calculate_shifted_coordinates(
    base_lat: float,
    base_lon: float,
    index: int,
    shift_value: float,
    points_per_circle: int,
) -> tuple[float, float]:
    circle_level = 1
    total_points_so_far = 0  # Center point

    while total_points_so_far + (points_per_circle * circle_level) < index:
        total_points_so_far += points_per_circle * circle_level
        circle_level += 1

    # Position within the current circle; index starts from 1.
    position_in_circle = index - total_points_so_far - 1
    circle_radius = shift_value * circle_level
    angle = (position_in_circle * 2 * math.pi) / (points_per_circle * circle_level)

    lat_offset = circle_radius * math.cos(angle)
    lon_offset = circle_radius * math.sin(angle)

    return base_lat + lat_offset, base_lon + lon_offset


class SchoolLocationShifter(DatabaseManagerBase):
    """
    Shift school locations in the database so that they do not overlap with other schools.

    This class provides functionality to shift the geographical coordinates
    of schools stored in the database by a given value within a specified radius.
    """

    def __init__(self, shift_value: float = ShifterSettings.SHIFT_VALUE):
        """
        Args:
            shift_value (float): The value by which to shift the coordinates in degrees.
                                Default: 0.0001 (≈11 meters)
        """
        super().__init__()
        self.shift_value: float = shift_value

    def shift_school_locations(
        self,
    ) -> int:
        """
        Shift school locations by a specified value within a given radius.

        Returns:
            int: Number of schools that were shifted
        """
        schools_with_duplicates = self._get_schools_with_duplicate_coordinates()

        if not schools_with_duplicates:
            return 0

        location_groups = _group_schools_by_location(schools_with_duplicates)
        schools_to_shift = _prepare_school_shifts(location_groups, self.shift_value)

        return self._update_school_coordinates(schools_to_shift)

    def _get_schools_with_duplicate_coordinates(
        self, precision: int = 5
    ) -> list[tuple[Szkola, float, float]]:
        """
        Get all schools that share the same coordinates (rounded to given precision).

        Precision reference:
        - 5 decimal places ≈ 1.1 meters
        - 6 decimal places ≈ 0.11 meters
        - 4 decimal places ≈ 11 meters

        """
        session = self._ensure_session()
        lat = func.round(cast(func.ST_Y(Szkola.geom), Numeric), precision)
        lon = func.round(cast(func.ST_X(Szkola.geom), Numeric), precision)

        # Subquery: find coordinate pairs that appear more than once
        duplicate_coords_subquery = (
            select(lat.label("lat"), lon.label("lon"))
            .group_by(lat, lon)
            .having(func.count() > 1)
        )

        # Main query: get all schools with those duplicate coordinates
        # Return rounded coordinates to ensure consistent grouping
        statement = select(
            Szkola,
            lat.label("lat"),
            lon.label("lon"),
        ).where(
            tuple_(lat, lon).in_(duplicate_coords_subquery)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
        )

        results = session.exec(statement).all()
        # Convert Decimal to float for geometric calculations
        schools = [(school, float(lat), float(lon)) for school, lat, lon in results]  # pyright: ignore[reportAny]
        return schools

    def _update_school_coordinates(
        self, schools_to_shift: list[tuple[Szkola, float, float]]
    ) -> int:
        """
        Update school coordinates in the database.

        Args:
            schools_to_shift: List of (school, new_latitude, new_longitude) tuples

        Returns:
            Number of schools updated
        """
        if not schools_to_shift:
            return 0

        session = self._ensure_session()
        updated_count = 0

        for school, new_lat, new_lon in schools_to_shift:
            # Update PostGIS geometry column (lon, lat order for POINT)
            school.geom = create_geom_point(new_lon, new_lat)
            session.add(school)
            updated_count += 1

            if updated_count % 1000 == 0:
                # commit in batches to avoid large transactions
                logger.info(
                    f"Committed {updated_count} school location shifts so far..."
                )
                session.commit()

        # final commit for any remaining updates
        session.commit()

        return updated_count
