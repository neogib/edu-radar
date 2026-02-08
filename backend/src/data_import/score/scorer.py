import logging

from sqlmodel import col, func, select

from src.app.models.exam_results import Przedmiot, WynikE8
from src.app.models.schools import Szkola
from src.data_import.config.score import CalculationSettings, ScoreType
from src.data_import.score.types import WynikTable
from src.data_import.utils.db.session import DatabaseManagerBase

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
    _most_recent_year: int = 0
    _table_type: type[WynikTable]

    def __init__(self, score_type: ScoreType):
        super().__init__()
        self._subject_weights_map = score_type.subject_weights_map
        self._table_type = score_type.table_type
        self._schools_ids = []
        self._subjects = []

    def calculate_scores(self):
        session = self._ensure_session()
        try:
            self._initialize_required_data()
        except ValueError as e:
            logger.error(
                f"⚙️ Initialization error: {e}. Aborting school scoring process."
            )
            return
        processed_schools = 0

        for id in self._schools_ids:
            school = self._select_where(Szkola, Szkola.id == id)
            if not school:
                logger.error(
                    f"🔍 School with ID {id} not found in database. Cannot update score."
                )
                continue

            final_score = 0.0

            for subject in self._subjects:
                subject_score = self._calculate_subject_score(subject, id)
                if subject_score is None:  # skip this school and set score to NULL
                    # missing results for this school or no results in the most recent year
                    logger.info(
                        f"⏩ School ID {id} missing '{subject.nazwa}' results. Setting score to NULL."
                    )
                    school.wynik = None
                    session.add(school)
                    processed_schools += 1
                    break
                weight = self._subject_weights_map[subject.nazwa]
                final_score += subject_score * weight
            else:
                # Loop completed without break - all subjects processed
                if final_score == 0.0:
                    logger.warning(
                        f"⚠️ Final score for school (id: {id}) is 0. Possible missing data. Setting score to NULL."
                    )
                    school.wynik = None
                else:
                    school.wynik = final_score
                    logger.info(
                        f"🎯 Score updated for school (RSPO: {school.numer_rspo}): {final_score:.2f}"
                    )
                session.add(school)
                processed_schools += 1

            if processed_schools % 100 == 0:
                session.commit()
                logger.info(
                    f"💾 Committed scores for {processed_schools} schools so far..."
                )

        # Final commit after processing all schools
        session.commit()

    def _calculate_subject_score(
        self, subject: Przedmiot, school_id: int
    ) -> float | None:
        """
        Calculate score for a specific subject and school.

        Returns:
            float: The calculated score (0.0 if no valid data)
            None: If school has no results for this subject in the most recent year
        """
        session = self._ensure_session()
        statement = select(self._table_type).where(
            self._table_type.szkola_id == school_id,
            self._table_type.przedmiot_id == subject.id,
        )
        subject_results = list(session.exec(statement).all())

        subject_score, denominator_is_zero = _calculate_weighted_score(
            subject_results=subject_results,
            most_recent_year=self._most_recent_year,
        )

        if denominator_is_zero:  # this should not happen if data in database is correct, log it just in case to identify potential data issues
            logger.warning(
                f"🔢 Denominator is zero for school ID {school_id}, subject '{subject.nazwa}' (total 'liczba_zdajacych' is 0). Assigning score 0 for this subject."
            )

        return subject_score

    def _initialize_required_data(self):
        self._most_recent_year = self._get_most_recent_year()
        self._load_school_ids()
        self._load_subjects()

    def _load_school_ids(self):
        session = self._ensure_session()
        stmt = select(self._table_type.szkola_id).where(
            self._table_type.rok == self._most_recent_year
        )
        ids = session.exec(stmt).unique()
        if not ids:
            raise ValueError("No school IDs found in the database.")
        self._schools_ids = list(ids)

    def _load_subjects(self):
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
