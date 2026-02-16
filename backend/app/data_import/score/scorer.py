import logging
from collections import defaultdict
from typing import cast

from sqlalchemy import bindparam, update
from sqlmodel import Session, col, func, select

from app.data_import.config.score import CalculationSettings, ScoreType
from app.data_import.score.types import WynikTable
from app.data_import.utils.db.session import DatabaseManagerBase
from app.models.exam_results import Przedmiot, WynikE8
from app.models.schools import Szkola

logger = logging.getLogger(__name__)


def _get_result_value(result: WynikTable) -> float | None:
    if result.mediana is not None:
        return result.mediana

    # if there is no median use sredni_wynik for WynikEM and wynik_sredni for WynikE8
    mean_value = (
        result.wynik_sredni if isinstance(result, WynikE8) else result.sredni_wynik
    )
    if mean_value is None:
        return None

    # apply penalty for using mean instead of median
    return mean_value * CalculationSettings.MEAN_PENALTY


def _calculate_weighted_score(
    subject_results: list[WynikTable], most_recent_year: int
) -> tuple[float | None, bool]:
    """
    Calculate weighted score for a subject across years.

    Returns:
        tuple[float | None, bool]:
            - score (None when school should be skipped)
            - denominator_is_zero flag for logging
    """
    if not subject_results:
        return None, False

    max_year = max(result.rok for result in subject_results)
    if max_year != most_recent_year:
        return None, False

    numerator = 0.0
    denominator = 0.0
    for result in subject_results:
        value = _get_result_value(result)
        if value is None:
            continue

        decay = CalculationSettings.DECAY_FACTOR ** (max_year - result.rok)
        weight = result.liczba_zdajacych * decay

        numerator += value * weight
        denominator += weight

    if denominator == 0:
        return 0.0, True

    return numerator / denominator, False


class Scorer(DatabaseManagerBase):
    """
    Calculates normalized school scores (0-100) based on exam results.

    Scoring rules:
    - Only considers schools that have results for all subjects defined in the score type
    - Only considers schools that have results from the most recent year in the database
    - If a school has no results for ANY subject in the most recent year,
      its score is set to NULL (even if it has scores from previous years)
    - This handles cases where schools become inactive or skip exam cycles
    """

    _subject_weights_map: dict[str, float]
    _schools_ids: list[int]
    _subjects: list[Przedmiot]
    _subject_ids: list[int]
    _most_recent_year: int = 0
    _table_type: type[WynikTable]

    def __init__(self, score_type: ScoreType, session: Session | None = None):
        super().__init__(session=session)
        self._subject_weights_map = score_type.subject_weights_map
        self._table_type = score_type.table_type
        self._schools_ids = []
        self._subjects = []
        self._subject_ids = []

    def calculate_scores(self, commit: bool = True) -> None:
        session = self._ensure_session()

        try:
            self._initialize_required_data()
            indexed_results = self._load_indexed_results()
            score_payload = self._build_score_payload(indexed_results)
            self._bulk_update_scores(score_payload)
            if commit:
                session.commit()
        except Exception:
            session.rollback()
            logger.exception("❌ Score calculation failed. Rolling back changes.")
            raise

    def _initialize_required_data(self) -> None:
        self._most_recent_year = self._get_most_recent_year()
        self._load_school_ids()
        self._load_subjects()
        self._subject_ids = [
            subject.id for subject in self._subjects if subject.id is not None
        ]

    def _load_indexed_results(self) -> dict[int, dict[int, list[WynikTable]]]:
        session = self._ensure_session()

        statement = select(self._table_type).where(
            col(self._table_type.szkola_id).in_(self._schools_ids),
            col(self._table_type.przedmiot_id).in_(self._subject_ids),
        )

        results = session.exec(statement).all()

        indexed_results: dict[int, dict[int, list[WynikTable]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for result in results:
            indexed_results[result.szkola_id][result.przedmiot_id].append(result)

        return indexed_results

    def _build_score_payload(
        self, indexed_results: dict[int, dict[int, list[WynikTable]]]
    ) -> list[dict[str, float | int]]:
        score_payload: list[dict[str, float | int]] = []
        missing_subject_count = 0
        zero_score_count = 0
        denominator_zero_count = 0

        for school_id in self._schools_ids:
            final_score = 0.0
            school_results = indexed_results.get(school_id, {})

            for subject in self._subjects:
                subject_id = cast(int, subject.id)

                subject_results = school_results.get(subject_id, [])
                subject_score, denominator_is_zero = _calculate_weighted_score(
                    subject_results=subject_results,
                    most_recent_year=self._most_recent_year,
                )

                if denominator_is_zero:
                    denominator_zero_count += 1

                if subject_score is None:
                    missing_subject_count += 1
                    break

                weight = self._subject_weights_map[subject.nazwa]
                final_score += subject_score * weight
            else:
                if final_score == 0.0:
                    zero_score_count += 1
                    continue

                score_payload.append(
                    {
                        "school_id_param": school_id,
                        "score_param": final_score,
                    }
                )

        if denominator_zero_count:
            logger.warning(
                f"🔢 Denominator was zero for {denominator_zero_count} school/subject combinations."
            )

        logger.info(
            f"📊 Score summary ({self._table_type.__name__}, year: {self._most_recent_year}): updated={len(score_payload)}, missing_subject={missing_subject_count}, zero_score={zero_score_count}"
        )
        return score_payload

    def _bulk_update_scores(self, score_payload: list[dict[str, float | int]]) -> None:
        if not score_payload:
            logger.warning("⚠️ No valid scores to update.")
            return

        session = self._ensure_session()
        statement = (
            update(Szkola)
            .where(col(Szkola.id) == bindparam("school_id_param"))
            .values(wynik=bindparam("score_param"))
        )
        _ = session.connection().execute(statement, score_payload)

    def _load_school_ids(self) -> None:
        session = self._ensure_session()
        stmt = select(self._table_type.szkola_id).where(
            self._table_type.rok == self._most_recent_year
        )
        ids = list(session.exec(stmt).unique().all())
        if not ids:
            raise ValueError("No school IDs found in the database.")
        self._schools_ids = ids

    def _load_subjects(self) -> None:
        session = self._ensure_session()
        subject_names = list(self._subject_weights_map.keys())
        statement = select(Przedmiot).where(col(Przedmiot.nazwa).in_(subject_names))
        self._subjects = list(session.exec(statement).all())
        if not self._subjects:
            raise ValueError("No subjects found in the database.")
        elif len(self._subjects) != len(subject_names):
            raise ValueError(
                f"Not all subjects found in the database. Found: {self._subjects}. Expected: {subject_names}"
            )

    def _get_most_recent_year(self) -> int:
        session = self._ensure_session()
        return session.exec(select(func.max(self._table_type.rok))).one()
