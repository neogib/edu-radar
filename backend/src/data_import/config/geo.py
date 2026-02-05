from pathlib import Path
from typing import ClassVar, final


@final
class ShifterSettings:
    SHIFT_VALUE = 0.0001  # ≈11 meters
    POINTS_PER_CIRCLE = 6


@final
class GeocodingSettings:
    UUG_URL: str = "https://services.gugik.gov.pl/uug/"
    ULDK_URL: str = "https://uldk.gugik.gov.pl"
    SRID_WGS84: int = 4326  # EPSG code for WGS84 coordinate system
    CHECKPOINT_FILE: Path = Path(__file__).parent.parent / "data" / "geo_checkpoint.txt"
    # Geocoding - change Warsaw districts into "Warszawa"
    WARSAW_DISTRICTS: ClassVar = {
        "Wola",
        "Mokotów",
        "Ochota",
        "Praga-Północ",
        "Praga-Południe",
        "Żoliborz",
        "Ursynów",
        "Bemowo",
        "Bielany",
        "Białołęka",
        "Targówek",
        "Wawer",
        "Wilanów",
        "Śródmieście",
        "Rembertów",
        "Ursus",
        "Włochy",
    }
    POLAND_BIGGEST_CITIES: ClassVar = {"Łódź", "Poznań", "Kraków", "Wrocław"}
