from sqlmodel import Session, SQLModel, select

from app.services.exceptions import EntityNotFoundError


class BaseService[TModel: SQLModel]:
    def __init__(self, session: Session, model: type[TModel]) -> None:
        self.session: Session = session
        self.model: type[TModel] = model

    def _get_entity(self, entity_id: int) -> TModel:
        entity = self.session.get(self.model, entity_id)
        if not entity:
            raise EntityNotFoundError(
                entity_id=entity_id, model_name=self.model.__name__
            )
        return entity

    def _get_entities(self) -> list[TModel]:
        return list(self.session.exec(select(self.model)).all())
