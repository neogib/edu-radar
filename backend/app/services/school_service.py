import logging
from typing import cast

from fastapi import Request
from geoalchemy2 import WKBElement
from pydantic import TypeAdapter
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, col, select

from app.core.sqlalchemy_typing import orm_rel_attr
from app.data_import.utils.geo import get_coordinates_from_geom
from app.models.exam_results import WynikE8, WynikEM
from app.models.locations import Gmina, Miejscowosc, Powiat
from app.models.schools import Szkola
from app.schemas.filters import FilterParams
from app.schemas.schools import SzkolaPublicShort
from app.services.base_service import BaseService
from app.services.exceptions import EntityNotFoundError, SchoolLocationNotFoundError
from app.services.school_filters import build_schools_short_query

# Setup
school_list_adapter = TypeAdapter(list[SzkolaPublicShort])

logger = logging.getLogger(__name__)


class SchoolService(BaseService[Szkola]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Szkola)

    def get_school(self, school_id: int) -> Szkola:
        return self._get_entity(school_id)

    def get_school_short(self, school_id: int) -> SzkolaPublicShort:
        "Get basic infor about school just to display on map. Does not include relations to other tables, so it's faster to query. For just one school we can take all columns without performance issues."
        school = self.get_school(school_id)

        if not school.geom:
            raise SchoolLocationNotFoundError(school_id)

        point = get_coordinates_from_geom(cast(WKBElement, school.geom))
        return SzkolaPublicShort(
            id=school_id,
            nazwa=school.nazwa,
            longitude=point.x,
            latitude=point.y,
            wynik=school.wynik,
            typ=school.typ.nazwa,
            status=school.status_publicznoprawny.nazwa,
        )

    def get_school_with_relations(self, school_id: int) -> Szkola:
        stmt = (
            select(Szkola)
            .where(Szkola.id == school_id)
            .options(
                joinedload(orm_rel_attr(Szkola.typ)),
                joinedload(orm_rel_attr(Szkola.status_publicznoprawny)),
                joinedload(orm_rel_attr(Szkola.kategoria_uczniow)),
                joinedload(orm_rel_attr(Szkola.ulica)),
                joinedload(orm_rel_attr(Szkola.miejscowosc))
                .joinedload(orm_rel_attr(Miejscowosc.gmina))
                .joinedload(orm_rel_attr(Gmina.powiat))
                .joinedload(orm_rel_attr(Powiat.wojewodztwo)),
                selectinload(orm_rel_attr(Szkola.etapy_edukacji)),
                selectinload(orm_rel_attr(Szkola.ksztalcenie_zawodowe)),
                selectinload(orm_rel_attr(Szkola.wyniki_e8)).joinedload(
                    orm_rel_attr(WynikE8.przedmiot)
                ),
                selectinload(orm_rel_attr(Szkola.wyniki_em)).joinedload(
                    orm_rel_attr(WynikEM.przedmiot)
                ),
                selectinload(orm_rel_attr(Szkola.rankingi)),
            )
        )
        school = self.session.exec(stmt).first()
        if not school:
            raise EntityNotFoundError(entity_id=school_id, model_name=Szkola.__name__)
        school.wyniki_e8.sort(key=lambda w: (w.rok, w.przedmiot.nazwa))
        school.wyniki_em.sort(key=lambda w: (w.rok, w.przedmiot.nazwa))
        return school

    def get_schools(self) -> list[Szkola]:
        return self._get_entities()

    def get_schools_short(self, filters: FilterParams):
        stmt = build_schools_short_query(filters)

        rows = (
            self.session.connection().execute(stmt).mappings().all()
        )  # use execute from sqlalchemy Session to get mappings

        return [SzkolaPublicShort.model_validate(row) for row in rows]

    async def stream_schools(self, filters: FilterParams, request: Request):
        last_id = 0

        while True:
            # Keyset pagination is stable for streaming large/updated datasets.
            stmt = (
                build_schools_short_query(filters)
                .where(col(Szkola.id) > last_id)
                .order_by(col(Szkola.id))
            )
            rows = self.session.connection().execute(stmt).mappings().all()

            if not rows:
                break

            schools_chunk = school_list_adapter.validate_python(rows)
            yield (school_list_adapter.dump_json(schools_chunk) + b"\n")

            last_id = cast(int, rows[-1]["id"])

            # abort when client disconnects
            if await request.is_disconnected():
                logger.info("Client disconnected, stopping schools stream")
                break
