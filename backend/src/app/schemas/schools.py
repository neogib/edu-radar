from src.app.models.schools import (
    EtapEdukacjiBase,
    KategoriaUczniowBase,
    KsztalcenieZawodoweBase,
    StatusPublicznoprawnyBase,
    SzkolaAllData,
    SzkolaBase,
    TypSzkolyBase,
)
from src.app.schemas.exam_results import (
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
)
from src.app.schemas.locations import MiejscowoscPublicWithGmina, UlicaPublic
from src.app.schemas.mixins import APIResponseConfig
from src.app.schemas.ranking import RankingPublic


class SzkolaPublic(APIResponseConfig, SzkolaAllData):
    id: int


# Short version of Szkola for listing schools with minimal info
# Fields are compressed for minimal data transfer
class SzkolaPublicShort(SzkolaBase):
    id: int
    latitude: float
    longitude: float
    wynik: float | None
    typ: str
    status: str


class SzkolaPublicWithRelations(SzkolaPublic):
    etapy_edukacji: list["EtapEdukacjiPublic"]
    typ: "TypSzkolyPublic"
    status_publicznoprawny: "StatusPublicznoprawnyPublic"
    kategoria_uczniow: "KategoriaUczniowPublic"
    miejscowosc: MiejscowoscPublicWithGmina
    ulica: UlicaPublic | None
    ksztalcenie_zawodowe: list["KsztalcenieZawodowePublic"]
    wyniki_e8: list[WynikE8PublicWithPrzedmiot]
    wyniki_em: list[WynikEMPublicWithPrzedmiot]
    rankingi: list[RankingPublic]


class KsztalcenieZawodowePublic(KsztalcenieZawodoweBase):
    id: int


class EtapEdukacjiPublic(EtapEdukacjiBase):
    id: int


class KategoriaUczniowPublic(KategoriaUczniowBase):
    id: int


class TypSzkolyPublic(TypSzkolyBase):
    id: int


class StatusPublicznoprawnyPublic(StatusPublicznoprawnyBase):
    id: int
