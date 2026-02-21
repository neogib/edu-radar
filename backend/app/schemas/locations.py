from app.models.locations import (
    GminaBase,
    MiejscowoscBase,
    PowiatBase,
    UlicaBase,
    WojewodztwoBase,
)
from app.schemas.base import CustomBaseModel


class WojewodztwoPublic(CustomBaseModel, WojewodztwoBase):
    id: int


class PowiatPublic(CustomBaseModel, PowiatBase):
    id: int


class PowiatPublicWithWojewodztwo(PowiatPublic):
    wojewodztwo: WojewodztwoPublic


class GminaPublic(CustomBaseModel, GminaBase):
    id: int


class GminaPublicWithPowiat(GminaPublic):
    powiat: PowiatPublicWithWojewodztwo


class MiejscowoscPublic(CustomBaseModel, MiejscowoscBase):
    id: int


class MiejscowoscPublicWithGmina(MiejscowoscPublic):
    gmina: GminaPublicWithPowiat


class UlicaPublic(CustomBaseModel, UlicaBase):
    id: int
