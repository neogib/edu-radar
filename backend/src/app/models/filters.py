from pydantic import BaseModel

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
    vocation_training: list[KsztalcenieZawodowePublic]


FILTER_MODELS = {
    "school_types": TypSzkoly,
    "public_statuses": StatusPublicznoprawny,
    "student_categories": KategoriaUczniow,
    "vocation_training": KsztalcenieZawodowe,
}
