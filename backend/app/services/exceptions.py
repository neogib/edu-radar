class EntityNotFoundError(Exception):
    def __init__(self, entity_id: object, model_name: str) -> None:
        self.entity_id: object = entity_id
        self.model_name: str = model_name
        super().__init__(f"{model_name} with id={entity_id} not found")


class SchoolLocationNotFoundError(Exception):
    def __init__(self, school_id: int) -> None:
        self.school_id: int = school_id
        super().__init__(f"School location with id={school_id} not found")
