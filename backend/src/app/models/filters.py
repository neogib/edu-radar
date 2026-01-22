from pydantic import BaseModel, Field

from src.app.models.schools import (
    KategoriaUczniow,
    KategoriaUczniowPublic,
    KsztalcenieZawodowe,
    KsztalcenieZawodowePublic,
    StatusPublicznoprawny,
    StatusPublicznoprawnyPublic,
    TypSzkoly,
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
    min_lng: float | None = Field(None, ge=-180, le=180)
    min_lat: float | None = Field(None, ge=-90, le=90)
    max_lng: float | None = Field(None, ge=-180, le=180)
    max_lat: float | None = Field(None, ge=-90, le=90)
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
    limit: int | None = Field(None, ge=1, le=1000)
