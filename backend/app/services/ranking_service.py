from math import ceil

from pydantic import TypeAdapter
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, func, select

from app.core.sqlalchemy_typing import orm_rel_attr
from app.models.locations import Gmina, Miejscowosc, Powiat, Wojewodztwo
from app.models.ranking import Ranking, RodzajRankingu
from app.models.schools import StatusPublicznoprawny, Szkola
from app.schemas.locations import PowiatPublic, WojewodztwoPublic
from app.schemas.ranking import (
    RankingDirection,
    RankingSchoolsStatus,
    RankingScope,
    RankingsFiltersResponse,
    RankingsParams,
    RankingsResponse,
    RankingWithSchool,
)
from app.schemas.schools import StatusPublicznoprawnyPublic
from app.services.base_service import BaseService

voivodeships_adapter = TypeAdapter(list[WojewodztwoPublic])
counties_adapter = TypeAdapter(list[PowiatPublic])
ranking_with_school_adapter = TypeAdapter(list[RankingWithSchool])
statuses_adapter = TypeAdapter(list[StatusPublicznoprawnyPublic])


class RankingService(BaseService[Ranking]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ranking)

    def get_ranking_filters(self) -> RankingsFiltersResponse:
        years = list(
            self.session.exec(
                select(Ranking.rok).distinct().order_by(col(Ranking.rok).desc())
            ).all()
        )
        voivodeships = voivodeships_adapter.validate_python(
            self.session.exec(select(Wojewodztwo).order_by(Wojewodztwo.nazwa)).all()
        )
        counties = counties_adapter.validate_python(
            self.session.exec(
                select(Powiat).order_by(col(Powiat.wojewodztwo_id), Powiat.nazwa)
            ).all()
        )

        statuses = statuses_adapter.validate_python(
            self.session.exec(
                select(StatusPublicznoprawny).where(
                    col(StatusPublicznoprawny.nazwa).in_(
                        [status.value for status in RankingSchoolsStatus]
                    )
                )
            ).all()
        )

        return RankingsFiltersResponse(
            years=years,
            scopes=list(RankingScope),
            types=list(RodzajRankingu),
            directions=list(RankingDirection),
            voivodeships=voivodeships,
            counties=counties,
            statuses=statuses,
        )

    def get_rankings_page(self, params: RankingsParams) -> RankingsResponse:
        where_conditions = [
            col(Ranking.rok) == params.year,
            col(Ranking.rodzaj_rankingu) == params.type,
        ]

        if params.search:
            where_conditions.append(
                col(Szkola.nazwa).ilike(f"%{params.search.strip()}%")
            )

        if params.status_id:
            where_conditions.append(
                col(Szkola.status_publicznoprawny_id) == params.status_id
            )

        if params.scope == RankingScope.WOJEWODZTWO:
            where_conditions.append(col(Powiat.wojewodztwo_id) == params.voivodeship_id)
        elif params.scope == RankingScope.POWIAT:
            where_conditions.append(col(Powiat.id) == params.county_id)

        count_stmt = (
            select(func.count(col(Ranking.id))).select_from(Ranking).join(Szkola)
        )
        if params.scope != RankingScope.KRAJ:
            count_stmt = count_stmt.join(Miejscowosc).join(Gmina).join(Powiat)
        count_stmt = count_stmt.where(*where_conditions)
        total = self.session.exec(count_stmt).one()

        order_column = col(Ranking.miejsce_kraj)
        if params.scope == RankingScope.WOJEWODZTWO:
            order_column = col(Ranking.miejsce_wojewodztwo)
        elif params.scope == RankingScope.POWIAT:
            order_column = col(Ranking.miejsce_powiat)

        offset = (params.page - 1) * params.page_size
        rows_stmt = select(Ranking).join(Szkola)
        if params.scope != RankingScope.KRAJ:
            rows_stmt = rows_stmt.join(Miejscowosc).join(Gmina).join(Powiat)
        rows_stmt = (
            rows_stmt.where(*where_conditions)
            .options(
                joinedload(orm_rel_attr(Ranking.szkola)).joinedload(
                    orm_rel_attr(Szkola.status_publicznoprawny),
                ),
                joinedload(orm_rel_attr(Ranking.szkola)).joinedload(
                    orm_rel_attr(Szkola.miejscowosc)
                ),
            )
            .order_by(
                order_column.asc()
                if params.direction == RankingDirection.BEST
                else order_column.desc(),
                col(Ranking.szkola_id),
            )
            .offset(offset)
            .limit(params.page_size)
        )

        rankings = list(self.session.exec(rows_stmt).all())
        ranking_rows = ranking_with_school_adapter.validate_python(
            rankings, from_attributes=True
        )

        return RankingsResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=ceil(total / params.page_size) if total else 0,
            rankings=ranking_rows,
        )
