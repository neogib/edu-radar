from enum import Enum
from typing import final

from app.models.exam_results import WynikE8, WynikEM


@final
class ScoreType(Enum):
    E8 = (
        {
            "język polski": 0.25,
            "matematyka": 0.5,
            "język angielski": 0.25,
        },
        WynikE8,
    )
    EM = (
        {
            "język polski poziom podstawowy": 0.25,
            "matematyka poziom podstawowy": 0.5,
            "język angielski poziom podstawowy": 0.25,
        },
        WynikEM,
    )

    def __init__(
        self, subject_weights_map: dict[str, float], table_type: type[WynikE8 | WynikEM]
    ):
        self.subject_weights_map = subject_weights_map
        self.table_type = table_type


@final
class CalculationSettings:
    MEAN_PENALTY = 0.7  # 30% penalty for subject with no median
    DECAY_FACTOR = 0.7  # 20% decline per year in score calculation
