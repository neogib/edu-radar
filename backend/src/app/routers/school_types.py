from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, select

from src.app.models.schools import TypSzkoly
from src.app.schemas.schools import TypSzkolyPublic
from src.dependencies import SessionDep

router = APIRouter(
    prefix="/school_types",
    tags=["school_types"],
)


@router.get("/", response_model=list[TypSzkolyPublic])
async def read_school_types(
    session: SessionDep,
    names: Annotated[
        list[str] | None, Query(description="Filter by school type names")
    ] = None,
):
    """
    Fetch all available school types or school types filtered by a list of names.
    """
    statement = select(TypSzkoly)
    if names:
        statement = statement.where(col(TypSzkoly.nazwa).in_(names))
    school_types = session.exec(statement).all()

    if names and not school_types:
        raise HTTPException(status_code=404, detail="School types not found")

    return school_types


@router.get("/{school_type_id}", response_model=TypSzkolyPublic)
async def read_school_type_by_id(school_type_id: int, session: SessionDep):
    school_type = session.get(TypSzkoly, school_type_id)
    if not school_type:
        raise HTTPException(status_code=404, detail="School type not found")
    return school_type
