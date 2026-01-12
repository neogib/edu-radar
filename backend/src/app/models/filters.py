from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field

from src.app.models.bounding_box import BoundingBox
from src.app.models.schools import (
    KategoriaUczniow,
    KategoriaUczniowPublic,
    StatusPublicznoprawny,
    StatusPublicznoprawnyPublic,
    TypSzkoly,
    TypSzkolyPublic,
)
from src.dependencies import parse_bbox


class FiltersResponse(BaseModel):
    school_types: list[TypSzkolyPublic]
    public_statuses: list[StatusPublicznoprawnyPublic]
    student_categories: list[KategoriaUczniowPublic]


FILTER_MODELS = {
    "school_types": TypSzkoly,
    "public_statuses": StatusPublicznoprawny,
    "student_categories": KategoriaUczniow,
}
