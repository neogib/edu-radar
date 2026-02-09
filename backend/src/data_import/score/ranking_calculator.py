import logging
from dataclasses import dataclass
from enum import Enum
from typing import cast
from unicodedata import normalize

from sqlalchemy import delete
from sqlmodel import col, func, select

from src.app.models.exam_results import WynikE8, WynikEM
from src.app.models.locations import Gmina, Miejscowosc, Powiat
from src.app.models.ranking import Ranking, RodzajRankingu
from src.app.models.schools import Szkola, TypSzkoly
from src.data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class _EmSchoolGroup(Enum):
    TECH = "TECH"
    LO = "LO"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class _SchoolData:
    school_id: int
    score: float
    wojewodztwo_id: int
    powiat_id: int


@dataclass(frozen=True)
class _PositionData:
    position: int
    population_size: int


def _normalize_text(value: str) -> str:
    """Normalize text for robust school-type matching."""
    normalized = normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_only.casefold()


def _classify_em_school_type(type_name: str) -> _EmSchoolGroup:
    """
    Split EM schools into ranking groups.

    Rules:
    - Technikum -> separate ranking
    - Branżowa szkoła II stopnia -> excluded
    - Everything else -> liceum ranking group
    """
    normalized = _normalize_text(type_name)

    if "technikum" in normalized:
        return _EmSchoolGroup.TECH

    is_branzowa_ii = (
        "branzowa" in normalized
        and "stopnia" in normalized
        and ("ii" in normalized or "2" in normalized)
    )
    if is_branzowa_ii:
        return _EmSchoolGroup.EXCLUDED

    return _EmSchoolGroup.LO


def _calculate_percentile(position: int, population_size: int) -> float:
    return (position / population_size) * 100.0


def _calculate_positions(schools: list[_SchoolData]) -> dict[int, _PositionData]:
    sorted_schools = sorted(
        schools,
        key=lambda school: (-school.score, school.school_id),
    )

    population_size = len(sorted_schools)
    return {
        school.school_id: _PositionData(position=index, population_size=population_size)
        for index, school in enumerate(sorted_schools, start=1)
    }


def _group_by_powiat(schools: list[_SchoolData]) -> dict[int, list[_SchoolData]]:
    grouped: dict[int, list[_SchoolData]] = {}
    for school in schools:
        grouped.setdefault(school.powiat_id, []).append(school)
    return grouped


def _group_by_wojewodztwo(schools: list[_SchoolData]) -> dict[int, list[_SchoolData]]:
    grouped: dict[int, list[_SchoolData]] = {}
    for school in schools:
        grouped.setdefault(school.wojewodztwo_id, []).append(school)
    return grouped


class RankingCalculator(DatabaseManagerBase):
    """Build ranking rows for the latest available E8/EM year."""

    def calculate_rankings(self) -> None:
        session = self._ensure_session()

        latest_e8_year = self._get_most_recent_exam_year(WynikE8)
        latest_em_year = self._get_most_recent_exam_year(WynikEM)

        e8_schools = self._load_e8_schools(latest_e8_year)
        self._replace_rankings(
            schools=e8_schools,
            year=latest_e8_year,
            ranking_type=RodzajRankingu.E8,
        )

        em_schools = self._load_em_schools(latest_em_year)
        tech_schools, lo_schools = self._split_em_schools_by_type(em_schools)

        self._replace_rankings(
            schools=tech_schools,
            year=latest_em_year,
            ranking_type=RodzajRankingu.EM_TECH,
        )
        self._replace_rankings(
            schools=lo_schools,
            year=latest_em_year,
            ranking_type=RodzajRankingu.EM_LO,
        )

        session.commit()
        logger.info("🎉 Ranking calculation completed")

    def _replace_rankings(
        self,
        schools: list[_SchoolData],
        year: int,
        ranking_type: RodzajRankingu,
    ) -> None:
        session = self._ensure_session()
        self._delete_existing_rankings(year, ranking_type)

        if not schools:
            logger.warning(
                f"⚠️ No schools found for ranking {ranking_type.value} in year {year}."
            )
            return

        national_positions = _calculate_positions(schools)

        wojewodztwo_positions: dict[int, dict[int, _PositionData]] = {}
        for woj_id, woj_schools in _group_by_wojewodztwo(schools).items():
            wojewodztwo_positions[woj_id] = _calculate_positions(woj_schools)

        powiat_positions: dict[int, dict[int, _PositionData]] = {}
        for powiat_id, powiat_schools in _group_by_powiat(schools).items():
            powiat_positions[powiat_id] = _calculate_positions(powiat_schools)

        ranking_rows: list[Ranking] = []
        for school in schools:
            kraj_data = national_positions[school.school_id]
            woj_data = wojewodztwo_positions[school.wojewodztwo_id][school.school_id]
            powiat_data = powiat_positions[school.powiat_id][school.school_id]

            ranking_rows.append(
                Ranking(
                    rok=year,
                    rodzaj_rankingu=ranking_type,
                    wynik=school.score,
                    szkola_id=school.school_id,
                    percentyl_kraj=_calculate_percentile(
                        kraj_data.position, kraj_data.population_size
                    ),
                    miejsce_kraj=kraj_data.position,
                    liczba_szkol_kraj=kraj_data.population_size,
                    percentyl_wojewodztwo=_calculate_percentile(
                        woj_data.position, woj_data.population_size
                    ),
                    miejsce_wojewodztwo=woj_data.position,
                    liczba_szkol_wojewodztwo=woj_data.population_size,
                    percentyl_powiat=_calculate_percentile(
                        powiat_data.position, powiat_data.population_size
                    ),
                    miejsce_powiat=powiat_data.position,
                    liczba_szkol_powiat=powiat_data.population_size,
                )
            )

        session.add_all(ranking_rows)
        session.flush()

        logger.info(
            f"✅ Created {len(ranking_rows)} ranking rows for {ranking_type.value} ({year})."
        )

    def _split_em_schools_by_type(
        self,
        schools: list[tuple[_SchoolData, str]],
    ) -> tuple[list[_SchoolData], list[_SchoolData]]:
        technical: list[_SchoolData] = []
        liceum_and_other: list[_SchoolData] = []
        excluded = 0

        for school, type_name in schools:
            group = _classify_em_school_type(type_name)
            if group is _EmSchoolGroup.EXCLUDED:
                excluded += 1
                continue
            if group is _EmSchoolGroup.TECH:
                technical.append(school)
                continue
            liceum_and_other.append(school)

        if excluded:
            logger.info(
                f"⏭️ Excluded {excluded} schools from EM ranking (Branżowa szkoła II stopnia)."
            )

        return technical, liceum_and_other

    def _delete_existing_rankings(
        self, year: int, ranking_type: RodzajRankingu
    ) -> None:
        session = self._ensure_session()
        statement = delete(Ranking).where(
            col(Ranking.rok) == year,
            col(Ranking.rodzaj_rankingu) == ranking_type,
        )
        _ = session.exec(statement)

    def _get_most_recent_exam_year(self, exam_model: type[WynikE8 | WynikEM]) -> int:
        session = self._ensure_session()
        statement = select(func.max(exam_model.rok))
        return session.exec(statement).one()

    def _load_e8_schools(self, year: int) -> list[_SchoolData]:
        session = self._ensure_session()

        statement = (
            select(
                Szkola.id,
                Szkola.wynik,
                Powiat.id,
                Powiat.wojewodztwo_id,
            )
            .join(WynikE8)
            .join(Miejscowosc)
            .join(Gmina)
            .join(Powiat)
            .where(
                WynikE8.rok == year,
                Szkola.wynik != None,  # noqa: E711
            )
            .distinct()
        )

        rows = cast(list[tuple[int, float, int, int]], session.exec(statement).all())
        schools: list[_SchoolData] = [
            _SchoolData(
                school_id=school_id,
                score=score,
                powiat_id=powiat_id,
                wojewodztwo_id=wojewodztwo_id,
            )
            for school_id, score, powiat_id, wojewodztwo_id in rows
        ]

        logger.info(f"📌 Loaded {len(schools)} E8 schools for year {year}.")
        return schools

    def _load_em_schools(self, year: int) -> list[tuple[_SchoolData, str]]:
        session = self._ensure_session()

        statement = (  # pyright: ignore[reportUnknownVariableType]
            select(  # pyright: ignore[reportCallIssue, reportUnknownMemberType]
                Szkola.id,
                Szkola.wynik,
                Powiat.id,
                Powiat.wojewodztwo_id,
                TypSzkoly.nazwa,
            )
            .join(WynikEM)
            .join(Miejscowosc)
            .join(Gmina)
            .join(Powiat)
            .join(TypSzkoly)
            .where(
                WynikEM.rok == year,
                col(Szkola.wynik).is_not(None),
            )
            .distinct()
        )

        rows = cast(
            list[tuple[int, float, int, int, str]],
            session.exec(statement).all(),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        )
        schools: list[tuple[_SchoolData, str]] = [
            (
                _SchoolData(
                    school_id=school_id,
                    score=score,
                    powiat_id=powiat_id,
                    wojewodztwo_id=wojewodztwo_id,
                ),
                type_name,
            )
            for school_id, score, powiat_id, wojewodztwo_id, type_name in rows
        ]

        logger.info(f"📌 Loaded {len(schools)} EM schools for year {year}.")
        return schools
