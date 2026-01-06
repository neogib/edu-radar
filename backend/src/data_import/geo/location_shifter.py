import math

from sqlmodel import Numeric, cast, func, select, tuple_

from src.app.models.schools import Szkola
from src.data_import.core.config import ShifterSettings
from src.data_import.utils.db.session import DatabaseManagerBase


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

        location_groups = self._group_schools_by_location(schools_with_duplicates)
        schools_to_shift = self._prepare_school_shifts(location_groups)

        return self._update_school_coordinates(schools_to_shift)

    def _get_schools_with_duplicate_coordinates(
        self, precision: int = 5
    ) -> list[Szkola]:
        """
        Get all schools that share the same coordinates (rounded to given precision).

        Precision reference:
        - 5 decimal places ≈ 1.1 meters
        - 6 decimal places ≈ 0.11 meters
        - 4 decimal places ≈ 11 meters

        """
        session = self._ensure_session()
        lat = func.round(cast(Szkola.geolokalizacja_latitude, Numeric), precision)
        lon = func.round(cast(Szkola.geolokalizacja_longitude, Numeric), precision)
        # Subquery: find coordinate pairs that appear more than once
        duplicate_coords_subquery = (
            select(lat.label("lat"), lon.label("lon"))
            .group_by("lat", "lon")
            .having(func.count() > 1)
            .subquery()
        )

        # Main query: get all schools with those duplicate coordinates
        statement = (
            select(Szkola)
            .where(tuple_(lat, lon).in_(duplicate_coords_subquery))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
            .order_by(
                Szkola.geolokalizacja_latitude,  # pyright: ignore[reportArgumentType]
                Szkola.geolokalizacja_longitude,  # pyright: ignore[reportArgumentType]
                Szkola.id,  # pyright: ignore[reportArgumentType]
            )
        )

        schools = list(session.exec(statement).all())
        return schools

    def _group_schools_by_location(
        self, schools: list[Szkola]
    ) -> dict[tuple[float, float], list[Szkola]]:
        """
        Group schools by their exact coordinates.

        Args:
            schools: List of schools to group

        Returns:
            Dictionary mapping coordinate tuples to lists of schools at those coordinates
        """

        location_groups: dict[tuple[float, float], list[Szkola]] = {}
        for school in schools:
            if (
                school.geolokalizacja_latitude == 0.0
                or school.geolokalizacja_longitude == 0.0
            ):
                # Skip invalid coordinates
                continue
            coords = (school.geolokalizacja_latitude, school.geolokalizacja_longitude)
            location_groups.setdefault(coords, []).append(school)

        return location_groups

    def _prepare_school_shifts(
        self,
        location_groups: dict[tuple[float, float], list[Szkola]],
    ) -> list[tuple[Szkola, float, float]]:
        """
        Prepare coordinate shifts for schools that need to be moved.

        Args:
            location_groups: Groups of schools by location

        Returns:
            List of tuples containing (school, new_latitude, new_longitude)
        """
        schools_to_shift: list[tuple[Szkola, float, float]] = []

        for coords, schools_at_location in location_groups.items():
            if len(schools_at_location) <= 1:
                continue

            # Keep the first school, shift the rest
            base_lat, base_lon = coords

            for i, school in enumerate(schools_at_location[1:], start=1):
                new_lat, new_lon = self._calculate_shifted_coordinates(
                    base_lat, base_lon, i
                )
                schools_to_shift.append((school, new_lat, new_lon))

        return schools_to_shift

    def _calculate_shifted_coordinates(
        self,
        base_lat: float,
        base_lon: float,
        index: int,
    ) -> tuple[float, float]:
        """
        Calculate shifted coordinates for a school using concentric circles.

        Points are arranged in circles with equal spacing between them.
        When a circle is full, a new wider circle level is created.

        Args:
            base_lat: Base latitude
            base_lon: Base longitude
            index: Index of the school in the duplicate group (1-based)

        Returns:
            Tuple of (new_latitude, new_longitude)
        """
        # Calculate which circle level and position within that circle
        # Circle 1: 6 points (indices 0-6)
        # Circle 2: 12 points (indices 7-18)
        # Circle 3: 18 points (indices 19-36)
        # Pattern: circle n has 6*n points

        circle_level = 1
        total_points_so_far = 0  # Center point

        while (
            total_points_so_far + (ShifterSettings.POINTS_PER_CIRCLE * circle_level)
            < index
        ):
            total_points_so_far += ShifterSettings.POINTS_PER_CIRCLE * circle_level
            circle_level += 1

        # Position within the current circle
        position_in_circle = index - total_points_so_far - 1  # starting index is 1

        # Radius for this circle level
        circle_radius = self.shift_value * circle_level

        # Angle for this position (evenly distributed around the circle)
        angle = (position_in_circle * 2 * math.pi) / (
            ShifterSettings.POINTS_PER_CIRCLE * circle_level
        )

        # Convert polar coordinates to Cartesian offsets
        lat_offset = circle_radius * math.cos(angle)
        lon_offset = circle_radius * math.sin(angle)

        # Apply offsets to base coordinates
        new_lat = base_lat + lat_offset
        new_lon = base_lon + lon_offset

        return new_lat, new_lon

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
            school.geolokalizacja_latitude = new_lat
            school.geolokalizacja_longitude = new_lon
            session.add(school)
            updated_count += 1

        session.commit()

        return updated_count
