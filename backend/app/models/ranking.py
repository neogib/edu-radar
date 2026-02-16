from enum import Enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import (
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)

if TYPE_CHECKING:
    from app.models.schools import Szkola


class RodzajRankingu(Enum):
    E8 = "E8"
    EM_LO = "EM_LO"
    EM_TECH = "EM_TECH"


class RankingBase(SQLModel):
    rok: int = Field(index=True, ge=2000)

    rodzaj_rankingu: RodzajRankingu = Field(
        sa_column=Column(
            sa.Enum(RodzajRankingu, name="rodzaj_rankingu"),
            nullable=False,
            index=True,
        )
    )

    wynik: float = Field(ge=0.0, le=100.0, index=True)

    # KRAJ
    percentyl_kraj: float = Field(ge=0.0, le=100.0, index=True)
    miejsce_kraj: int = Field(ge=1, index=True)
    liczba_szkol_kraj: int = Field(ge=1)

    # WOJEWÓDZTWO
    percentyl_wojewodztwo: float = Field(ge=0.0, le=100.0, index=True)
    miejsce_wojewodztwo: int = Field(ge=1, index=True)
    liczba_szkol_wojewodztwo: int = Field(ge=1)

    # POWIAT
    percentyl_powiat: float = Field(ge=0.0, le=100.0, index=True)
    miejsce_powiat: int = Field(ge=1, index=True)
    liczba_szkol_powiat: int = Field(ge=1)

    # foreign_key
    szkola_id: int = Field(foreign_key="szkola.id", index=True)


class Ranking(RankingBase, table=True):
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint(
            "szkola_id",
            "rok",
            "rodzaj_rankingu",
            name="uq_ranking_szkola_rok_rodzaj",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    szkola: "Szkola" = Relationship(back_populates="rankingi")  # pyright: ignore[reportAny]
