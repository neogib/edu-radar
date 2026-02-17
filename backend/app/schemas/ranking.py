from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.models.ranking import RankingBase, RodzajRankingu
from app.schemas.schools import SzkolaPublicRankingRow


class RankingScope(Enum):
    KRAJ = "KRAJ"
    WOJEWODZTWO = "WOJEWODZTWO"
    POWIAT = "POWIAT"


class RankingDirection(Enum):
    BEST = "BEST"
    WORST = "WORST"


class RankingPublic(RankingBase):
    id: int


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Requested page number")
    page_size: int = Field(
        100, ge=1, le=200, description="Number of items per page (max 200)"
    )


class RankingsParams(PaginationParams):
    rok: int = Field(ge=2000)
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
        None, description="Required if zakres_rankingu is WOJEWODZTWO"
    )
    county_id: int | None = Field(
        None, description="Required if zakres_rankingu is POWIAT"
    )

    @model_validator(mode="after")
    def validate_ranking_scope_ids(self) -> Self:
        if self.scope == RankingScope.WOJEWODZTWO and self.voivodeship_id is None:
            raise ValueError(
                "wojewodztwo_id is required when zakres_rankingu is WOJEWODZTWO"
            )
        if self.scope == RankingScope.POWIAT and self.county_id is None:
            raise ValueError("powiat_id is required when zakres_rankingu is POWIAT")
        return self


class RankingSchoolRow(RankingPublic, SzkolaPublicRankingRow):
    pass


class RankingsResponse(BaseModel):
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(
        ge=1,
        le=200,
        description="Number of items per page (can differ from requested page_size if fewer items are available)",
    )
    total: int = Field(
        ge=0, description="Total number of schools matching the ranking params criteria"
    )
    total_pages: int = Field(
        ge=0, description="Total number of pages available based on the page_size"
    )
    schools: list[RankingSchoolRow]
