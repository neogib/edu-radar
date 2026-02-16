# pyright: reportUnknownParameterType = false
# pyright: reportUnknownMemberType = false
# pyright: reportUnknownVariableType = false
# pyright: reportMissingTypeArgument = false
# pyright: reportUnknownArgumentType = false
import logging
from collections.abc import Hashable
from typing import cast

import pandas as pd
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import col, select

from app.data_import.config.excel import ExamType, ExcelFile
from app.data_import.utils.clean_column_names import (
    clean_column_name,
    clean_subjects_names,
)
from app.data_import.utils.db.session import DatabaseManagerBase
from app.models.exam_results import (
    Przedmiot,
    WynikE8,
    WynikE8Extra,
    WynikEM,
    WynikEMExtra,
)
from app.models.schools import Szkola

logger = logging.getLogger(__name__)


ResultPayload = dict[str, int | float | None]


def _extract_rspo_col_name(exam_data: pd.DataFrame) -> tuple[str, str]:
    rspo_cols = [
        col
        for col in exam_data.columns
        if isinstance(col, tuple)
        and "RSPO" in col[1]  # RSPO is in the second part of the tuple
    ]
    if len(rspo_cols) != 1:
        raise ValueError("Exactly one column with 'RSPO' in its name is expected.")
    return cast(tuple[str, str], rspo_cols[0])


def _extract_subject_names(exam_data: pd.DataFrame) -> set[str]:
    unique_subjects: set[str] = set()
    for column in exam_data.columns:
        # Check if it's a tuple (multi-index) and not unnamed/metadata column which can be skipped
        if isinstance(column, tuple) and len(column) > 1:
            valid_col = True
            for col_prefix in ExcelFile.SPECIAL_COLUMN_START:
                if col_prefix in column[0]:
                    valid_col = False
                    break
            if not valid_col:
                continue
            unique_subjects.add(str(column[0]))

    return unique_subjects


class TableSplitter(DatabaseManagerBase):
    exam_data: pd.DataFrame
    rspo_col_name: tuple[str, str] = ("", "")
    unique_subjects: set[str]
    exam_type: ExamType
    year: int
    subjects_cache: dict[str, Przedmiot]
    processed_count: int = 0
    skipped_schools: int = 0
    added_results: int = 0
    school_ids_by_rspo: dict[int, int]
    _pending_e8_rows: list[ResultPayload]
    _pending_em_rows: list[ResultPayload]
    _bulk_flush_size: int = 10_000

    def __init__(self, exam_data: pd.DataFrame, exam_type: ExamType, year: int):
        super().__init__()
        self.exam_data = exam_data
        self.exam_type = exam_type
        self.year = year
        self.unique_subjects = set()
        self.subjects_cache = {}
        self.school_ids_by_rspo = {}
        self._pending_e8_rows = []
        self._pending_em_rows = []

    def initialize(self) -> bool:
        """Perform initialization and validation steps.
        Returns True if successful, False otherwise."""
        try:
            self.rspo_col_name = _extract_rspo_col_name(self.exam_data)
            self._get_subjects_names()
            return True
        except ValueError as e:
            logger.error(
                f"❌ Initialization failed: {e}. Skipping processing for this file."
            )
            return False

    def split_exam_results(self):
        """
        Iterates through exam data, finds corresponding schools and subjects,
        creates WynikE8/WynikEM records, and adds them to the DB session.
        """
        logger.info(
            f"📊 Starting processing of {self.exam_type} results for {len(self.exam_data)} schools..."
        )
        session = self._ensure_session()
        self._prefetch_school_ids()

        for index, school_exam_data in self.exam_data.iterrows():
            school_exam_data: pd.Series
            try:
                # Find School by RSPO
                rspo = self.get_school_rspo_number(school_exam_data, index)
                if not rspo:
                    continue

                school_id = self.school_ids_by_rspo.get(rspo)
                if school_id is None:
                    self.skip_school(
                        f"❌ School with RSPO {rspo} not found in database for row {index}"
                    )
                    continue

                # Process results for each subject for this school
                self.create_results(school_exam_data, school_id, rspo)

                self.processed_count += 1
                if self.processed_count % 100 == 0:  # Log progress periodically
                    logger.info(
                        f"⏳ Processed {self.processed_count} schools... Added {self.added_results} results so far."
                    )

            except Exception as e:
                logger.exception(f"📛 Unexpected error processing row {index}: {e}")
                self.skipped_schools += (
                    1  # Count as skipped if major error occurs for the row
                )

        self._flush_pending_results()
        session.commit()
        logger.info(f"✅ Successfully processed {self.processed_count} schools.")
        logger.info(f"Added {self.added_results} new exam results to the database.")
        logger.info(
            f"Skipped {self.skipped_schools} schools due to missing/invalid RSPO, school not found in DB, or row processing error."
        )

    def create_results(self, school_exam_data: pd.Series, school_id: int, rspo: int):
        results_buffered = 0
        for subject_name in self.unique_subjects:
            subject = self.get_subject(clean_subjects_names(subject_name))

            subject_exam_result = cast(
                ResultPayload,
                (school_exam_data.loc[subject_name]).to_dict(),  # pyright: ignore[reportAny]
            )
            # logger.info(
            #     f"Processing exam result for subject '{subject.nazwa}' (School RSPO: {rspo}): {subject_exam_result}"
            # )
            # change numpy NaN values to None and clean column names
            subject_exam_result = {
                clean_column_name(k): (v if pd.notna(v) else None)
                for k, v in subject_exam_result.items()
            }

            match self.exam_type:
                case ExamType.E8:
                    result_payload = self.create_result_record(
                        subject_exam_result,
                        school_id,
                        rspo,
                        subject,
                        WynikE8Extra,
                    )
                case ExamType.EM:
                    result_payload = self.create_result_record(
                        subject_exam_result,
                        school_id,
                        rspo,
                        subject,
                        WynikEMExtra,
                    )
            if not result_payload:
                continue  # there was a ValidationError or insufficient data
            match self.exam_type:
                case ExamType.E8:
                    self._pending_e8_rows.append(result_payload)
                case ExamType.EM:
                    self._pending_em_rows.append(result_payload)
            results_buffered += 1

        if (
            len(self._pending_e8_rows) + len(self._pending_em_rows)
            >= self._bulk_flush_size
        ):
            self._flush_pending_results()

    def create_result_record(
        self,
        subject_exam_result: ResultPayload,
        school_id: int,
        rspo: int,
        subject: Przedmiot,
        base: type[WynikE8Extra | WynikEMExtra],
    ) -> ResultPayload | None:
        session = self._ensure_session()
        try:
            result_base = base.model_validate(subject_exam_result)
        except ValidationError as e:
            logger.error(
                f"🚫 Invalid data for subject '{subject.nazwa}' (School RSPO: {rspo}). Details: {subject_exam_result}. Error: {e}"
            )
            return None
        if not self._validate_enough_data(
            result_base
        ):  # skip results with insufficient data
            return None

        if subject.id is None:
            session.flush()

        return {
            "szkola_id": school_id,
            "przedmiot_id": subject.id,
            "rok": self.year,
            **result_base.model_dump(),
        }

    def get_subject(self, subject_name: str) -> Przedmiot:
        """Gets a Przedmiot record in the database. If it does not exist, creates it."""
        if subject_name in self.subjects_cache:
            return self.subjects_cache[subject_name]

        subject = self._select_where(Przedmiot, Przedmiot.nazwa == subject_name)
        if subject:
            self.subjects_cache[subject_name] = subject
            return subject

        # no record found
        self.create_subject(subject_name)
        return self.subjects_cache[subject_name]

    def create_subject(self, subject_name: str):
        """Creates a Przedmiot record in the database."""
        logger.info(f"✨ Creating new subject (Przedmiot): {subject_name}")
        session = self._ensure_session()
        subject = Przedmiot(nazwa=subject_name)
        self.subjects_cache[subject_name] = subject
        session.add(subject)

    def _flush_pending_results(self) -> None:
        session = self._ensure_session()

        if self._pending_e8_rows:
            stmt_e8 = (
                pg_insert(WynikE8)
                .on_conflict_do_nothing(
                    index_elements=["szkola_id", "przedmiot_id", "rok"]
                )
                .returning(col(WynikE8.szkola_id))
            )
            result_e8 = session.exec(stmt_e8, params=self._pending_e8_rows)
            self.added_results += sum(1 for _ in result_e8)
            logger.info(f"⬇️ Flushed {len(self._pending_e8_rows)} WynikE8 rows.")
            self._pending_e8_rows.clear()

        if self._pending_em_rows:
            stmt_em = (
                pg_insert(WynikEM)
                .on_conflict_do_nothing(
                    index_elements=["szkola_id", "przedmiot_id", "rok"]
                )
                .returning(col(WynikEM.szkola_id))
            )
            result_em = session.exec(stmt_em, params=self._pending_em_rows)
            self.added_results += sum(1 for _ in result_em)
            logger.info(f"⬇️ Flushed {len(self._pending_em_rows)} WynikEM rows.")
            self._pending_em_rows.clear()

    def get_school_rspo_number(
        self, school_exam_data: pd.Series, index: Hashable
    ) -> int | None:
        # Extract RSPO number from the current row
        rspo = school_exam_data.at[self.rspo_col_name]

        if pd.isna(rspo):
            self.skip_school(f"❓ RSPO number not found in row {index}")
            return None
        return int(cast(str | int | float, rspo))

    def skip_school(self, reason: str):
        logger.warning(
            f"{reason}. Therefore, skipping associated results for this school."
        )
        self.skipped_schools += 1

    @staticmethod
    def _validate_enough_data(result: WynikE8Extra | WynikEMExtra) -> bool:
        # the columns differ in different exam types
        average_score: float | None = (
            result.sredni_wynik
            if isinstance(result, WynikEMExtra)
            else result.wynik_sredni
        )
        if (
            not result.liczba_zdajacych
        ):  # even if liczba_zdajacych is 0 we are dismissing the result
            return False
        if average_score is None and result.mediana is None:  # score can equal to 0
            return False
        return True

    def _get_subjects_names(self):
        """
        Extracts unique subject names from the multi-level column index,
        prunes exam data to include only subjects of interest.
        Assumes subject names are in the first level.
        """

        self.unique_subjects = _extract_subject_names(self.exam_data)

        logger.info(f"📚 Identified subjects for processing: {self.unique_subjects}")
        cols_to_keep = [*self.unique_subjects, self.rspo_col_name[0]]

        # slicing of self.exam_data to get only exam results + rspo column
        self.exam_data = self.exam_data.loc[:, cols_to_keep]

    def _prefetch_school_ids(self) -> None:
        session = self._ensure_session()
        rspo_values: list[int | str | float] = (
            self.exam_data[self.rspo_col_name].dropna().tolist()
        )
        unique_rspos: set[int] = set()
        for rspo in rspo_values:
            try:
                unique_rspos.add(int(rspo))
            except (TypeError, ValueError):
                continue

        if not unique_rspos:
            return

        rspo_list = list(unique_rspos)
        rows = session.exec(
            select(Szkola.numer_rspo, Szkola.id).where(
                col(Szkola.numer_rspo).in_(rspo_list)
            )
        ).all()
        for school_rspo, school_id in rows:
            assert school_id is not None
            self.school_ids_by_rspo[school_rspo] = school_id

        logger.info(
            f"🏫 Prefetched {len(self.school_ids_by_rspo)} school IDs for {len(unique_rspos)} RSPO values."
        )
