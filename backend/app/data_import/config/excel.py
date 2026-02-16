from enum import Enum
from typing import Final, final

EM_FORMULA_PRIORITY: Final[dict[str, int]] = {"EM2023": 0, "EM2015": 1}


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
