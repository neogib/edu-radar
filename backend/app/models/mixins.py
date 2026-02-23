from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Field, SQLModel


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=_now_utc,
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=_now_utc,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        },
    )
