class EntityNotFoundError(Exception):
    def __init__(self, entity_id: object, model_name: str) -> None:
        self.entity_id: object = entity_id
        self.model_name: str = model_name
        super().__init__(f"{model_name} with id={entity_id} not found")


class SchoolLocationNotFoundError(Exception):
    def __init__(self, school_id: int) -> None:
        self.school_id: int = school_id
        super().__init__(f"School location with id={school_id} not found")


class TurnstileServiceUnavailableError(Exception):
    pass


class TurnstileVerificationFailedError(Exception):
    def __init__(self, error_codes: list[str]) -> None:
        self.error_codes: list[str] = error_codes
        super().__init__("Turnstile verification failed")
