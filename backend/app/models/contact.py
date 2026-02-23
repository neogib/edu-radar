from sqlmodel import Field, SQLModel

from app.models.mixins import TimestampMixin


class KontaktBase(SQLModel):
    name: str = Field(max_length=120)
    email: str = Field(max_length=254)
    topic: str = Field(max_length=150)
    message: str = Field(max_length=2000)
    turnstile_token: str = Field(max_length=2048)


class Kontakt(KontaktBase, TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
