from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import TypeAdapter
from sqlmodel import Session

from src.app.models.exam_results import (
    WynikE8PublicWithPrzedmiot,  # noqa: F401
    WynikEMPublicWithPrzedmiot,  # noqa: F401
)
from src.app.schemas.filters import FilterParams
from src.app.models.schools import (
    Szkola,
    SzkolaPublicShort,
    SzkolaPublicWithRelations,
)
from src.app.services.map_school_to_public import to_public_short
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
    offset = 0

    while True:
        stmt = apply_filters(filters).limit(CHUNK_SIZE).offset(offset)
        rows = session.exec(stmt).all()
        schools = [to_public_short(szkola, lat, lon) for szkola, lat, lon in rows]

        if not schools:
            break

        batch = school_list_adapter.validate_python(schools, from_attributes=True)
        yield school_list_adapter.dump_json(batch) + b"\n"

        offset += CHUNK_SIZE

        # abort when client disconnects
        if await request.is_disconnected():
            print("client disconnected, stopping stream")
            break


@router.get("/{school_id}", response_model=SzkolaPublicWithRelations)
async def read_school(school_id: int, session: SessionDep) -> Szkola:
    school = session.get(Szkola, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.get("/", response_model=list[SzkolaPublicShort])
async def read_schools(session: SessionDep, filters: Annotated[FilterParams, Query()]):
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

    rows = session.exec(stmt).all()
    schools = [to_public_short(szkola, lat, lon) for szkola, lat, lon in rows]
    return schools
