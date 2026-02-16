from typing import ClassVar, Literal, Self, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.schools import (
    KategoriaUczniow,
    KsztalcenieZawodowe,
    StatusPublicznoprawny,
    TypSzkoly,
)
from app.schemas.schools import (
    KategoriaUczniowPublic,
    KsztalcenieZawodowePublic,
    StatusPublicznoprawnyPublic,
    TypSzkolyPublic,
)


class FiltersResponse(BaseModel):
    school_types: list[TypSzkolyPublic]
    public_statuses: list[StatusPublicznoprawnyPublic]
    student_categories: list[KategoriaUczniowPublic]
    vocational_training: list[KsztalcenieZawodowePublic]


FILTER_MODELS = {
    "school_types": TypSzkoly,
    "public_statuses": StatusPublicznoprawny,
    "student_categories": KategoriaUczniow,
    "vocational_training": KsztalcenieZawodowe,
}


class FilterParams(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True
    )
    min_lng: float | None = Field(None, ge=-180, le=180, alias="minLng")
    min_lat: float | None = Field(None, ge=-90, le=90, alias="minLat")
    max_lng: float | None = Field(None, ge=-180, le=180, alias="maxLng")
    max_lat: float | None = Field(None, ge=-90, le=90, alias="maxLat")
    bbox_mode: Literal["within", "outside"] = "within"
    q: str | None = Field(
        None, min_length=2, description="Search query for school name"
    )
    type_id: list[int] | None = Field(
        None, description="Filter by school type IDs", alias="type"
    )
    status_id: list[int] | None = Field(
        None, description="Filter by public/private status IDs", alias="status"
    )
    category_id: list[int] | None = Field(
        None, description="Filter by student category IDs", alias="category"
    )
    vocational_training_id: list[int] | None = Field(
        None, description="Filter by vocational training IDs", alias="career"
    )
    min_score: int | None = Field(None, ge=0, le=100)
    max_score: int | None = Field(None, ge=0, le=100)
    closed: bool = Field(
        False, description="Include closed/liquidated schools in the results"
    )
    limit: int | None = Field(None, ge=1, le=1000)

    @model_validator(mode="after")
    def validate_bbox(self) -> Self:
        present = [
            self.min_lng is not None,
            self.min_lat is not None,
            self.max_lng is not None,
            self.max_lat is not None,
        ]
        if any(present) and not all(present):
            raise ValueError("All bbox parameters must be provided together")
        if all(present):
            if cast(float, self.min_lat) >= cast(float, self.max_lat):
                raise ValueError("max_lat must be greater than min_lat")
            if cast(float, self.min_lng) >= cast(float, self.max_lng):
                raise ValueError("max_lng must be greater than min_lng")
        return self
