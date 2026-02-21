from pydantic import TypeAdapter
from sqlmodel import Session, select

from app.models.schools import (
    KategoriaUczniow,
    KsztalcenieZawodowe,
    StatusPublicznoprawny,
    TypSzkoly,
)
from app.schemas.school_filters import SchoolFiltersResponse
from app.schemas.schools import (
    KategoriaUczniowPublic,
    KsztalcenieZawodowePublic,
    StatusPublicznoprawnyPublic,
    TypSzkolyPublic,
)

school_types_adapter = TypeAdapter(list[TypSzkolyPublic])
public_statuses_adapter = TypeAdapter(list[StatusPublicznoprawnyPublic])
student_categories_adapter = TypeAdapter(list[KategoriaUczniowPublic])
vocational_training_adapter = TypeAdapter(list[KsztalcenieZawodowePublic])


def get_filter_options(session: Session) -> SchoolFiltersResponse:
    school_types = school_types_adapter.validate_python(
        session.exec(select(TypSzkoly).order_by(TypSzkoly.nazwa)).all()
    )
    public_statuses = public_statuses_adapter.validate_python(
        session.exec(
            select(StatusPublicznoprawny).order_by(StatusPublicznoprawny.nazwa)
        ).all()
    )
    student_categories = student_categories_adapter.validate_python(
        session.exec(select(KategoriaUczniow).order_by(KategoriaUczniow.nazwa)).all()
    )
    vocational_training = vocational_training_adapter.validate_python(
        session.exec(
            select(KsztalcenieZawodowe).order_by(KsztalcenieZawodowe.nazwa)
        ).all()
    )

    return SchoolFiltersResponse(
        school_types=school_types,
        public_statuses=public_statuses,
        student_categories=student_categories,
        vocational_training=vocational_training,
    )
