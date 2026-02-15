from typing import cast

from geoalchemy2 import WKBElement
from geoalchemy2.shape import (
    from_shape,  # pyright: ignore[reportUnknownVariableType]
    to_shape,
)
from shapely.geometry import Point

from src.data_import.config.geo import GeocodingSettings


def create_geom_point(lon: float, lat: float) -> WKBElement:
    return from_shape(Point(lon, lat), srid=GeocodingSettings.SRID_WGS84)


def get_coordinates_from_geom(geom: WKBElement) -> Point:
    return cast(Point, to_shape(geom))


def normalize_city_name(city: str) -> str:
    if city in GeocodingSettings.WARSAW_DISTRICTS:
        return "Warszawa"

    # districts start with "CityName-", for example "Wrocław-Psie Pole"
    for big_city in GeocodingSettings.POLAND_BIGGEST_CITIES:
        if city.startswith(f"{big_city}-"):
            return big_city

    return city


def build_full_address(
    city: str, street: str | None = None, building_number: str | None = None
) -> str:
    full_address = city
    if street:
        full_address += f", {street}"
    if building_number:
        full_address += f" {building_number}"
    return full_address
