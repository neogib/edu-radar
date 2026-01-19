from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import col, exists, select

from src.app.models.bounding_box import BoundingBox
from src.app.models.exam_results import (
    WynikE8PublicWithPrzedmiot,  # noqa: F401
    WynikEMPublicWithPrzedmiot,  # noqa: F401
)
from src.app.models.schools import (
    Szkola,
    SzkolaKsztalcenieZawodoweLink,
    SzkolaPublicShort,
    SzkolaPublicWithRelations,
)
from src.dependencies import SessionDep, parse_bbox

_ = SzkolaPublicWithRelations.model_rebuild()


router = APIRouter(
    prefix="/schools",
    tags=["schools"],
)


@router.get("/{school_id}", response_model=SzkolaPublicWithRelations)
async def read_school(school_id: int, session: SessionDep) -> Szkola:
    school = session.get(Szkola, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


class FilterParams(BoundingBox):
    type: int | None = None


@router.get("/", response_model=list[SzkolaPublicShort])
async def read_schools(
    session: SessionDep,
    bbox: Annotated[BoundingBox | None, Depends(parse_bbox)],
    q: Annotated[
        str | None,
        Query(min_length=2, description="Search query for school name", alias="q"),
    ] = None,
    type_id: Annotated[
        list[int] | None, Query(description="Filter by school type IDs", alias="type")
    ] = None,
    status_id: Annotated[
        list[int] | None,
        Query(description="Filter by public/private status IDs", alias="status"),
    ] = None,
    category_id: Annotated[
        list[int] | None,
        Query(description="Filter by student category IDs", alias="category"),
    ] = None,
    vocational_training_id: Annotated[
        list[int] | None,
        Query(
            description="Filter by vocational training IDs", alias="vocational_training"
        ),
    ] = None,
    min_score: Annotated[int | None, Query(ge=0, le=100)] = None,
    max_score: Annotated[int | None, Query(ge=0, le=100)] = None,
    limit: Annotated[int | None, Query(ge=1, le=1000)] = None,
):
    """
    Get schools within bounding box with optional filters.

    ## Filter Logic
    - Filters are combined with AND logic between different filter types
    - Multiple values within the same filter use OR logic
    - Example: `typ_id=1&typ_id=2&status_id=1` means
      (type 1 OR type 2) AND (status 1)
    """

    # SQL query to filter schools within bounding box boundaries
    statement = select(Szkola).options(
        selectinload(Szkola.typ),  # pyright: ignore [reportArgumentType]
        selectinload(Szkola.status_publicznoprawny),  # pyright: ignore [reportArgumentType]
    )

    if q:
        statement = statement.where(col(Szkola.nazwa).ilike(f"%{q}%"))

    if bbox:
        statement = statement.where(
            (Szkola.geolokalizacja_latitude >= bbox.min_lat)
            & (Szkola.geolokalizacja_latitude <= bbox.max_lat)
            & (Szkola.geolokalizacja_longitude >= bbox.min_lng)
            & (Szkola.geolokalizacja_longitude <= bbox.max_lng)
        )

    # Apply filters based on query parameters
    if type_id:
        statement = statement.where(col(Szkola.typ_id).in_(type_id))

    if status_id:
        statement = statement.where(
            col(Szkola.status_publicznoprawny_id).in_(status_id)
        )

    if category_id:
        statement = statement.where(col(Szkola.kategoria_uczniow_id).in_(category_id))

    if vocational_training_id:
        statement = statement.where(
            exists(
                select(1).where(
                    SzkolaKsztalcenieZawodoweLink.szkola_id == Szkola.id,
                    col(SzkolaKsztalcenieZawodoweLink.ksztalcenie_zawodowe_id).in_(
                        vocational_training_id
                    ),
                )
            )
        )

    if min_score is not None:
        statement = statement.where(col(Szkola.score) >= min_score)
    if max_score is not None:
        statement = statement.where(col(Szkola.score) <= max_score)

    if limit:
        statement = statement.limit(limit)
    elif q:
        statement = statement.limit(50)

    schools = session.exec(statement).all()
    return schools
