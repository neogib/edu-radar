# pyright: reportUnknownVariableType = false
# pyright: reportUnknownArgumentType = false
# pyright: reportUnknownMemberType = false
from sqlalchemy import Select
from sqlmodel import col, exists, func, select

from app.models.locations import Miejscowosc
from app.models.schools import (
    StatusPublicznoprawny,
    Szkola,
    SzkolaKsztalcenieZawodoweLink,
    TypSzkoly,
)
from app.schemas.school_filters import SchoolFilterParams


def build_schools_short_query(
    filters: SchoolFilterParams,
) -> Select[tuple[int, str, float | None, str, str, float, float, str]]:
    """
    Apply filters to the Szkola query based on the provided SchoolFilterParams.
    """
    statement = (
        select(  # pyright: ignore[reportCallIssue]
            col(Szkola.id),
            col(Szkola.nazwa),
            col(Szkola.wynik),
            col(TypSzkoly.nazwa).label("typ"),
            col(StatusPublicznoprawny.nazwa).label("status"),
            func.ST_Y(Szkola.geom).label("latitude"),
            func.ST_X(Szkola.geom).label("longitude"),
            col(Miejscowosc.nazwa).label("miejscowosc"),
        )
        .join(TypSzkoly)
        .join(StatusPublicznoprawny)
        .join(Miejscowosc)
    )

    if not filters.closed:
        statement = statement.where(~(col(Szkola.zlikwidowana)))

    present = [
        filters.min_lng is not None,
        filters.min_lat is not None,
        filters.max_lng is not None,
        filters.max_lat is not None,
    ]

    # bounding box filters allow getting schools within or outside the box
    if all(present):  # all four bbox parameters are provided
        envelope = func.ST_MakeEnvelope(
            filters.min_lng,
            filters.min_lat,
            filters.max_lng,
            filters.max_lat,
            4326,
        )

        if filters.bbox_mode == "within":
            statement = statement.where(col(Szkola.geom).op("&&")(envelope))

        elif filters.bbox_mode == "outside":
            statement = statement.where(~col(Szkola.geom).op("&&")(envelope))
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
                    col(SzkolaKsztalcenieZawodoweLink.szkola_id) == col(Szkola.id),
                    col(SzkolaKsztalcenieZawodoweLink.ksztalcenie_zawodowe_id).in_(
                        filters.vocational_training_id
                    ),
                )
            )
        )

    if filters.min_score is not None:
        statement = statement.where(col(Szkola.wynik) >= filters.min_score)
    if filters.max_score is not None:
        statement = statement.where(col(Szkola.wynik) <= filters.max_score)

    # query search for school name
    if filters.q:
        statement = statement.where(col(Szkola.nazwa).ilike(f"%{filters.q}%"))

    if filters.limit:  # used for example when fetching live suggestions
        statement = statement.limit(filters.limit)

    return statement
