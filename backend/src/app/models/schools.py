# pyright: reportAny = false
from datetime import date
from typing import TYPE_CHECKING, Optional  # pyright: ignore[reportDeprecated]

from geoalchemy2 import Geometry
from sqlmodel import (
    Column,
    Field,
    Relationship,
    SQLModel,
)

from src.app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from src.app.models.exam_results import (
        WynikE8,
        WynikEM,
    )
    from src.app.models.locations import Miejscowosc, Ulica
    from src.app.models.ranking import Ranking


class TypSzkolyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class TypSzkoly(TypSzkolyBase, table=True):
    __tablename__: str = "typ_szkoly"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="typ")


class StatusPublicznoprawnyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class StatusPublicznoprawny(StatusPublicznoprawnyBase, table=True):
    __tablename__: str = "status_publicznoprawny"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="status_publicznoprawny")


class KategoriaUczniowBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class KategoriaUczniow(KategoriaUczniowBase, table=True):
    __tablename__: str = "kategoria_uczniow"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="kategoria_uczniow")


# link table for connecting EtapyEdukacji and Szkoly
class SzkolaEtapLink(SQLModel, table=True):
    etap_id: int | None = Field(
        default=None, foreign_key="etap_edukacji.id", primary_key=True
    )
    szkola_id: int | None = Field(
        default=None, foreign_key="szkola.id", primary_key=True
    )


class EtapEdukacjiBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class EtapEdukacji(EtapEdukacjiBase, table=True):
    __tablename__: str = "etap_edukacji"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(
        back_populates="etapy_edukacji", link_model=SzkolaEtapLink
    )


class SzkolaKsztalcenieZawodoweLink(SQLModel, table=True):
    ksztalcenie_zawodowe_id: int | None = Field(
        default=None, foreign_key="ksztalcenie_zawodowe.id", primary_key=True
    )
    szkola_id: int | None = Field(
        default=None, foreign_key="szkola.id", primary_key=True
    )


class KsztalcenieZawodoweBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class KsztalcenieZawodowe(KsztalcenieZawodoweBase, table=True):
    __tablename__: str = "ksztalcenie_zawodowe"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(
        back_populates="ksztalcenie_zawodowe", link_model=SzkolaKsztalcenieZawodoweLink
    )


class SzkolaBase(SQLModel):
    nazwa: str = Field(index=True)


class SzkolaExtendedData(SzkolaBase):  # used in SzkolaAPIResponse
    numer_rspo: int = Field(unique=True, index=True)
    nazwa_skrocona: str | None = Field(default=None, index=True)
    nip: str | None = Field(default=None)
    regon: str | None = Field(default=None, unique=True)
    liczba_uczniow: int | None = Field(default=None, ge=0)
    dyrektor_imie: str | None = Field(default=None)
    dyrektor_nazwisko: str | None = Field(default=None)
    kod_pocztowy: str | None = Field(default=None)
    numer_budynku: str | None = Field(default=None)
    numer_lokalu: str | None = Field(default=None)
    telefon: str | None = Field(
        default=None,
    )
    email: str | None = Field(
        default=None,
    )
    strona_internetowa: str | None = Field(default=None)
    data_zalozenia: date | None = Field(default=None)
    data_rozpoczecia: date | None = Field(default=None, index=True)
    data_likwidacji: date | None = Field(default=None, index=True)


class SzkolaAllData(SzkolaExtendedData):
    wynik: float | None = Field(default=None, ge=0.0, le=100.0, index=True)
    zlikwidowana: bool = Field(default=False, index=True)

    # Foreign keys
    typ_id: int = Field(index=True, foreign_key="typ_szkoly.id")
    status_publicznoprawny_id: int = Field(
        index=True, foreign_key="status_publicznoprawny.id"
    )
    kategoria_uczniow_id: int = Field(index=True, foreign_key="kategoria_uczniow.id")
    miejscowosc_id: int = Field(index=True, foreign_key="miejscowosc.id")
    ulica_id: int | None = Field(index=True, default=None, foreign_key="ulica.id")


class Szkola(SzkolaAllData, TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # geom only for spatial queries, not exposed in API
    geom: object = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    )

    # this column is a control flag for editing school visiblity
    # aktualna = "should this record be shown by default"
    aktualna: bool = Field(default=True, index=True)

    # Relationships - many-to-one
    typ: TypSzkoly = Relationship(back_populates="szkoly")
    status_publicznoprawny: StatusPublicznoprawny = Relationship(
        back_populates="szkoly"
    )
    kategoria_uczniow: KategoriaUczniow = Relationship(back_populates="szkoly")
    miejscowosc: "Miejscowosc" = Relationship(back_populates="szkoly")
    ulica: "Ulica | None" = Relationship(back_populates="szkoly")

    # Relationships - many-to-many
    etapy_edukacji: list[EtapEdukacji] = Relationship(
        back_populates="szkoly", link_model=SzkolaEtapLink
    )
    ksztalcenie_zawodowe: list[KsztalcenieZawodowe] = Relationship(
        back_populates="szkoly", link_model=SzkolaKsztalcenieZawodoweLink
    )
    wyniki_e8: list["WynikE8"] = Relationship(back_populates="szkola")
    wyniki_em: list["WynikEM"] = Relationship(back_populates="szkola")
    rankingi: list["Ranking"] = Relationship(back_populates="szkola")
