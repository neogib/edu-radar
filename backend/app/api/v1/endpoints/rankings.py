from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import SessionDep
from app.schemas.ranking import (
    RankingsFiltersResponse,
    RankingsParams,
    RankingsResponse,
)
from app.services.ranking_service import RankingService

router = APIRouter(
    prefix="/rankings",
    tags=["rankings"],
)


def get_ranking_service(session: SessionDep) -> RankingService:
    return RankingService(session)


RankingServiceDep = Annotated[RankingService, Depends(get_ranking_service)]


@router.get("/filters")
async def read_rankings_filters(service: RankingServiceDep) -> RankingsFiltersResponse:
    return service.get_ranking_filters()


@router.get("/")
async def read_rankings(
    service: RankingServiceDep,
    params: Annotated[RankingsParams, Query()],
) -> RankingsResponse:
    return service.get_rankings_page(params)
