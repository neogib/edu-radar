from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import col, exists, select

from src.app.models.exam_results import (
    WynikE8PublicWithPrzedmiot,  # noqa: F401
    WynikEMPublicWithPrzedmiot,  # noqa: F401
)
from src.app.models.filters import FilterParams
from src.app.models.schools import (
    Szkola,
    SzkolaKsztalcenieZawodoweLink,
    SzkolaPublicShort,
    SzkolaPublicWithRelations,
)
from src.dependencies import SessionDep

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

    # SQL query to filter schools within bounding box boundaries
    statement = select(Szkola).options(
        selectinload(Szkola.typ),  # pyright: ignore [reportArgumentType]
        selectinload(Szkola.status_publicznoprawny),  # pyright: ignore [reportArgumentType]
    )

    # bounding box filters
    if filters.min_lng:
        statement = statement.where(
            col(Szkola.geolokalizacja_longitude) >= filters.min_lng
        )
    if filters.max_lng:
        statement = statement.where(
            col(Szkola.geolokalizacja_latitude) <= filters.max_lng
        )
    if filters.min_lat:
        statement = statement.where(
            col(Szkola.geolokalizacja_longitude) >= filters.min_lat
        )
    if filters.max_lat:
        statement = statement.where(
            col(Szkola.geolokalizacja_latitude) <= filters.max_lat
        )
    # Apply filters based on query parameters
    if filters.type_id:
        statement = statement.where(col(Szkola.typ_id).in_(filters.type_id))

    if filters.status_id:
        statement = statement.where(
            col(Szkola.status_publicznoprawny_id).in_(filters.status_id)
        )

    if filters.category_id:
        statement = statement.where(
            col(Szkola.kategoria_uczniow_id).in_(filters.category_id)
        )

    if filters.vocational_training_id:
        statement = statement.where(
            exists(
                select(1).where(
                    SzkolaKsztalcenieZawodoweLink.szkola_id == Szkola.id,
                    col(SzkolaKsztalcenieZawodoweLink.ksztalcenie_zawodowe_id).in_(
                        filters.vocational_training_id
                    ),
                )
            )
        )

    if filters.min_score is not None:
        statement = statement.where(col(Szkola.score) >= filters.min_score)
    if filters.max_score is not None:
        statement = statement.where(col(Szkola.score) <= filters.max_score)

    # query search for school name
    if filters.q:
        statement = statement.where(col(Szkola.nazwa).ilike(f"%{filters.q}%"))

    if filters.limit:
        statement = statement.limit(
            filters.limit
        )  # for autocompletion not all results should be returned

    schools = session.exec(statement).all()
    return schools
