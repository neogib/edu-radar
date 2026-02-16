class SchoolNotFoundError(Exception):
    def __init__(self, school_id: int) -> None:
        self.school_id: int = school_id
        super().__init__(f"School with id={school_id} not found")


class SchoolLocationNotFoundError(Exception):
    def __init__(self, school_id: int) -> None:
        self.school_id: int = school_id
        super().__init__(f"School location with id={school_id} not found")
