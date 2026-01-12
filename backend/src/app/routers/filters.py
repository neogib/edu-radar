from fastapi import APIRouter
from sqlmodel import select

from src.app.models.filters import FILTER_MODELS, FiltersResponse
from src.dependencies import SessionDep

router = APIRouter(
    prefix="/filters",
    tags=["filters"],
)


@router.get("/")
async def read_filters(session: SessionDep) -> FiltersResponse:
    options = {
        key: session.exec(select(model)).all() for key, model in FILTER_MODELS.items()
    }

    return FiltersResponse.model_validate(options)
