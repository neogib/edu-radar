# pyright: reportAny = false
from typing import TYPE_CHECKING

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
)

if TYPE_CHECKING:
    from app.models.schools import Szkola


class WojewodztwoBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)


class Wojewodztwo(WojewodztwoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    powiaty: list["Powiat"] = Relationship(back_populates="wojewodztwo")


class PowiatBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    wojewodztwo_id: int = Field(index=True, foreign_key="wojewodztwo.id")


class Powiat(PowiatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    wojewodztwo: Wojewodztwo = Relationship(back_populates="powiaty")
    gminy: list["Gmina"] = Relationship(back_populates="powiat")


class GminaBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    powiat_id: int = Field(index=True, foreign_key="powiat.id")


class Gmina(GminaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    powiat: Powiat = Relationship(back_populates="gminy")
    miejscowosci: list["Miejscowosc"] = Relationship(back_populates="gmina")


class MiejscowoscBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    gmina_id: int = Field(index=True, foreign_key="gmina.id")


class Miejscowosc(MiejscowoscBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    gmina: Gmina = Relationship(back_populates="miejscowosci")
    szkoly: list["Szkola"] = Relationship(back_populates="miejscowosc")


class UlicaBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)


class Ulica(UlicaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="ulica")
