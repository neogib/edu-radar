from typing import Annotated, cast

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import TypeAdapter
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlmodel import col, select

from src.app.core.sqlalchemy_typing import orm_rel_attr
from src.app.models.exam_results import WynikE8, WynikEM
from src.app.models.locations import Gmina, Miejscowosc, Powiat
from src.app.models.schools import (
    Szkola,
)
from src.app.schemas.filters import FilterParams
from src.app.schemas.schools import SzkolaPublicShort, SzkolaPublicWithRelations
from src.app.services.school_filters import apply_filters
from src.dependencies import SessionDep

_ = SzkolaPublicWithRelations.model_rebuild()


router = APIRouter(
    prefix="/schools",
    tags=["schools"],
)


# Setup
school_list_adapter = TypeAdapter(list[SzkolaPublicShort])
CHUNK_SIZE = 1000


@router.get("/stream")
async def read_schools_stream(
    session: SessionDep, request: Request, filters: Annotated[FilterParams, Query()]
):
    filters.limit = CHUNK_SIZE  # to control chunk size in streaming
    return StreamingResponse(
        stream_schools(request, session, filters),
        media_type="application/x-ndjson",
    )


async def stream_schools(
    request: Request,
    session: Session,
    filters: FilterParams,
):
    last_id = 0

    while True:
        # Keyset pagination is stable for streaming large/updated datasets.
        stmt = (
            apply_filters(filters)
            .where(col(Szkola.id) > last_id)
            .order_by(col(Szkola.id))
        )
        rows = session.execute(stmt).mappings().all()

        if not rows:
            break

        schools_chunk = school_list_adapter.validate_python(rows)
        yield (school_list_adapter.dump_json(schools_chunk) + b"\n")

        last_id = cast(int, rows[-1]["id"])

        # abort when client disconnects
        if await request.is_disconnected():
            print("client disconnected, stopping stream")
            break


@router.get("/{school_id}", response_model=SzkolaPublicWithRelations)
async def read_school(school_id: int, session: SessionDep) -> Szkola:
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
    school = session.exec(stmt).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.get("/")
async def read_schools(
    session: SessionDep, filters: Annotated[FilterParams, Query()]
) -> list[SzkolaPublicShort]:
    """
    Get schools with optional filters.

    _**Note:**
    This endpoint should only be used for smaller amounts of data. To get all schools consider using `/school/stream` endpoint with StreamingResponse._

    ## Filter Logic
    - Filters are combined with AND logic between different filter types
    - Multiple values within the same filter use OR logic
    - Example: `type=1&typeid=2&status=1` means
      (type 1 OR type 2) AND (status 1)
    """

    stmt = apply_filters(filters)

    s = cast(Session, session)  # for better type checking
    rows = (
        s.execute(stmt).mappings().all()
    )  # use execute from sqlalchemy Session to get mappings

    schools = [SzkolaPublicShort.model_validate(row) for row in rows]
    return schools
