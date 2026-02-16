from app.models.exam_results import (
    PrzedmiotBase,
    WynikCommon,
    WynikE8Extra,
    WynikEMExtra,
)


class PrzedmiotPublic(PrzedmiotBase):
    id: int


class WynikE8Public(WynikCommon, WynikE8Extra):
    id: int


class WynikE8PublicWithPrzedmiot(WynikE8Public):
    przedmiot: PrzedmiotPublic


class WynikEMPublic(WynikCommon, WynikEMExtra):
    id: int


class WynikEMPublicWithPrzedmiot(WynikEMPublic):
    przedmiot: PrzedmiotPublic
