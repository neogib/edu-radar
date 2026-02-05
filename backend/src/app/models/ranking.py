from typing import TYPE_CHECKING

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)

if TYPE_CHECKING:
    from src.app.models.schools import Szkola


class RankingBase(SQLModel):
    rok: int = Field(index=True, ge=2000)

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


class Ranking(RankingBase, table=True):
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint(
            "szkola_id",
            "rok",
            name="uq_ranking_szkola_rok",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    szkola_id: int = Field(
        foreign_key="szkola.id",
        index=True,
    )

    szkola: "Szkola" = Relationship(back_populates="rankingi")  # pyright: ignore[reportAny]
