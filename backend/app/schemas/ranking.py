from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.models.ranking import RodzajRankingu
from app.schemas.base import CustomBaseModel
from app.schemas.locations import PowiatPublic, WojewodztwoPublic
from app.schemas.ranking_shared import RankingPublic
from app.schemas.schools import SzkolaRankingRow


class RankingScope(Enum):
    KRAJ = "KRAJ"
    WOJEWODZTWO = "WOJEWODZTWO"
    POWIAT = "POWIAT"


class RankingDirection(Enum):
    BEST = "BEST"
    WORST = "WORST"


class PaginationParams(CustomBaseModel):
    page: int = Field(1, ge=1, description="Requested page number")
    page_size: int = Field(
        50, ge=1, le=100, description="Number of items per page (max 100)"
    )


class RankingsParams(PaginationParams):
    year: int = Field(ge=2000)
    type: RodzajRankingu = Field(
        RodzajRankingu.E8,
        description="Ranking type: E8 (primary schools), EM_LO (matura results - high schools), EM_TECH (matura results - technical schools)",
    )
    scope: RankingScope = Field(
        RankingScope.KRAJ,
        description="Ranking scope: KRAJ (national), WOJEWODZTWO (voivodeship), POWIAT (county)",
    )
    direction: RankingDirection = Field(
        RankingDirection.BEST,
        description="Ranking order: BEST (top schools first) or WORST (lowest schools first)",
    )
    voivodeship_id: int | None = Field(
        None, description="Required if scope is WOJEWODZTWO"
    )
    county_id: int | None = Field(None, description="Required if scope is POWIAT")
    search: str | None = Field(
        None,
        description="Optional search term to filter schools by name (case-insensitive, partial match)",
    )

    @model_validator(mode="after")
    def validate_ranking_scope_ids(self) -> Self:
        if self.scope == RankingScope.WOJEWODZTWO and self.voivodeship_id is None:
            raise ValueError("voivodeship_id is required when scope is WOJEWODZTWO")
        if self.scope == RankingScope.POWIAT and self.county_id is None:
            raise ValueError("county_id is required when scope is POWIAT")
        return self


class RankingWithSchool(RankingPublic):
    szkola: SzkolaRankingRow


class RankingsResponse(CustomBaseModel):
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(
        le=100,
        description="Number of items per page",
    )
    total: int = Field(
        ge=0, description="Total number of schools matching the ranking params criteria"
    )
    total_pages: int = Field(
        ge=0, description="Total number of pages available based on the page_size"
    )
    rankings: list[RankingWithSchool]


class RankingsFiltersResponse(CustomBaseModel):
    years: list[int]
    scopes: list[RankingScope]
    types: list[RodzajRankingu]
    directions: list[RankingDirection]
    voivodeships: list[WojewodztwoPublic]
    counties: list[PowiatPublic]
