from sqlmodel import Session

from app.models.contact import Kontakt
from app.schemas.contact import ContactSubmitRequest
from app.services.base_service import BaseService


class ContactService(BaseService[Kontakt]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Kontakt)

    def create_contact(self, payload: ContactSubmitRequest) -> Kontakt:
        kontakt = Kontakt(
            name=payload.name,
            email=str(payload.email),
            topic=payload.topic,
            message=payload.message,
        )
        self.session.add(kontakt)
        self.session.commit()
        self.session.refresh(kontakt)
        return kontakt
