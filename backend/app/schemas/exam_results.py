from app.models.exam_results import (
    PrzedmiotBase,
    WynikCommon,
    WynikE8Extra,
    WynikEMExtra,
)
from app.schemas.base import CustomBaseModel


class PrzedmiotPublic(CustomBaseModel, PrzedmiotBase):
    id: int


class WynikE8Public(CustomBaseModel, WynikCommon, WynikE8Extra):
    id: int


class WynikE8PublicWithPrzedmiot(WynikE8Public):
    przedmiot: PrzedmiotPublic


class WynikEMPublic(CustomBaseModel, WynikCommon, WynikEMExtra):
    id: int


class WynikEMPublicWithPrzedmiot(WynikEMPublic):
    przedmiot: PrzedmiotPublic
