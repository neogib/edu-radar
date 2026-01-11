from enum import Enum
from pathlib import Path
from typing import ClassVar, final

from src.app.models.exam_results import WynikE8, WynikEM


class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/"
    HEADERS: ClassVar[dict[str, str]] = {"accept": "application/ld+json"}
    START_PAGE: int = 1
    PAGE_LIMIT: int | None = None  # the last page to fetch, if None there is no limit
    MAX_SCHOOLS_SEGMENT: int = 1000


class RetrySettings:
    INITIAL_DELAY: int = 1
    MAX_DELAY: int = 30
    MAX_RETRIES: int = 20


class TIMEOUT:
    CONNECT: int = 30
    READ: int = 60


class ShifterSettings:
    SHIFT_VALUE: float = 0.0001  # ≈11 meters
    POINTS_PER_CIRCLE: int = 6


@final
class ExamType(Enum):
    "Directories for E8 and EM data and their headers"

    E8 = ("E8_data", [0, 1], None)
    EM = ("EM_data", [1, 2], 0)

    def __init__(self, directory_name: str, header: list[int], skip_rows: int | None):
        self.directory_name = directory_name
        self.header = header
        self.skiprows = skip_rows


@final
class ExcelFile:
    SHEET_NAME = "SAS"
    SPECIAL_COLUMN_START = ("Unnamed", "dla")


@final
class ScoreType(Enum):
    E8 = (
        {
            "język polski": 0.3,
            "matematyka": 0.4,
            "język angielski": 0.3,
        },
        WynikE8,
    )
    EM = (
        {
            "język polski poziom podstawowy": 0.25,
            "matematyka poziom podstawowy": 0.3,
            "język angielski poziom podstawowy": 0.25,
            "język angielski poziom rozszerzony": 0.1,
            "matematyka poziom rozszerzony": 0.1,
        },
        WynikEM,
    )

    def __init__(
        self, subject_weights_map: dict[str, float], table_type: type[WynikE8 | WynikEM]
    ):
        self.subject_weights_map = subject_weights_map
        self.table_type = table_type


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "storage"
CSV_DIR = DATA_DIR / "csv"
LOGS_DIR = DATA_DIR / "logs"


@final
class GeocodingSettings:
    UUG_URL: str = "https://services.gugik.gov.pl/uug/"
    ULDK_URL: str = "https://uldk.gugik.gov.pl"
    SRID_POL: int = 2180  # EPSG code for Poland CS92 coordinate system
    SRID_WGS84: int = 4326  # EPSG code for WGS84 coordinate system
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
