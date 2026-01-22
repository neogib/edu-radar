from sqlalchemy.orm import selectinload
from sqlmodel import col, exists, select
from sqlmodel.sql.expression import SelectOfScalar

from src.app.models.filters import FilterParams
from src.app.models.schools import Szkola, SzkolaKsztalcenieZawodoweLink


def apply_filters(filters: FilterParams) -> SelectOfScalar[Szkola]:
    """
    Apply filters to the Szkola query based on the provided FilterParams.
    """
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

    return statement
