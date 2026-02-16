from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import SessionDep
from app.schemas.schools import TypSzkolyPublic
from app.services.school_type_service import SchoolTypeService

router = APIRouter(
    prefix="/school_types",
    tags=["school_types"],
)


def get_school_type_service(session: SessionDep) -> SchoolTypeService:
    return SchoolTypeService(session)


SchoolServiceDep = Annotated[SchoolTypeService, Depends(get_school_type_service)]


@router.get("/", response_model=list[TypSzkolyPublic])
async def read_school_types(
    service: SchoolServiceDep,
    names: Annotated[
        list[str] | None, Query(description="Filter by school type names")
    ] = None,
):
    """
    Fetch all available school types or school types filtered by a list of names.
    """
    if names:
        return service.get_school_types_by_names(names)
    return service.get_school_types()


@router.get("/{school_type_id}", response_model=TypSzkolyPublic)
async def read_school_type(school_type_id: int, service: SchoolServiceDep):
    """
    Fetch a single school type by its ID.
    """
    return service.get_school_type(school_type_id)
