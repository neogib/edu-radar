from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.school_filters import SchoolFiltersResponse
from app.services.filter_options import get_filter_options

router = APIRouter(
    prefix="/filters",
    tags=["filters"],
)


@router.get("/")
async def read_filters(session: SessionDep) -> SchoolFiltersResponse:
    return get_filter_options(session)
