from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.dependencies import SessionDep
from app.models.schools import (
    Szkola,
)
from app.schemas.filters import FilterParams
from app.schemas.schools import (
    SzkolaPublicShort,
    SzkolaPublicShortWithMiejscowosc,
    SzkolaPublicWithRelations,
)
from app.services.school_service import SchoolService

_ = SzkolaPublicWithRelations.model_rebuild()


router = APIRouter(
    prefix="/schools",
    tags=["schools"],
)


def get_school_service(session: SessionDep) -> SchoolService:
    return SchoolService(session)


SchoolServiceDep = Annotated[SchoolService, Depends(get_school_service)]


# const for schools streaming
CHUNK_SIZE = 1000


@router.get("/stream")
async def read_schools_stream(
    service: SchoolServiceDep,
    filters: Annotated[FilterParams, Query()],
    request: Request,
):
    filters.limit = CHUNK_SIZE  # to control chunk size in streaming
    return StreamingResponse(
        service.stream_schools(filters, request),
        media_type="application/x-ndjson",
    )


@router.get("/{school_id}/short")
async def read_school_short(
    school_id: int, service: SchoolServiceDep
) -> SzkolaPublicShort:
    return service.get_school_short(school_id)


@router.get("/live")
async def read_schools_live(
    service: SchoolServiceDep, filters: Annotated[FilterParams, Query()]
) -> list[SzkolaPublicShortWithMiejscowosc]:
    return service.get_schools_short_with_miejscowosc(filters)


@router.get("/{school_id}", response_model=SzkolaPublicWithRelations)
async def read_school(school_id: int, service: SchoolServiceDep) -> Szkola:
    return service.get_school_with_relations(school_id)


@router.get("/")
async def read_schools(
    service: SchoolServiceDep, filters: Annotated[FilterParams, Query()]
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
    return service.get_schools_short(filters)
