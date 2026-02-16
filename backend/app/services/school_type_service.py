from sqlmodel import Session, col, select

from app.models.schools import TypSzkoly
from app.services.base_service import BaseService


class SchoolTypeService(BaseService[TypSzkoly]):
    def __init__(self, session: Session):
        super().__init__(session, TypSzkoly)

    def get_school_type(self, school_type_id: int) -> TypSzkoly:
        return self._get_entity(school_type_id)

    def get_school_types(self) -> list[TypSzkoly]:
        return self._get_entities()

    def get_school_types_by_names(self, names: list[str]) -> list[TypSzkoly]:
        statement = select(TypSzkoly).where(col(TypSzkoly.nazwa).in_(names))
        return list(self.session.exec(statement).all())
