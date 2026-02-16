from fastapi import APIRouter
from sqlmodel import select

from app.dependencies import SessionDep
from app.schemas.filters import FILTER_MODELS, FiltersResponse

router = APIRouter(
    prefix="/filters",
    tags=["filters"],
)


@router.get("/")
async def read_filters(session: SessionDep) -> FiltersResponse:
    options = {
        key: session.exec(select(model).order_by(model.nazwa)).all()
        for key, model in FILTER_MODELS.items()
    }

    return FiltersResponse.model_validate(options)
