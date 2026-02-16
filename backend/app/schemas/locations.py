from app.models.locations import (
    GminaBase,
    MiejscowoscBase,
    PowiatBase,
    UlicaBase,
    WojewodztwoBase,
)


class WojewodztwoPublic(WojewodztwoBase):
    id: int


class PowiatPublic(PowiatBase):
    id: int


class PowiatPublicWithWojewodztwo(PowiatPublic):
    wojewodztwo: WojewodztwoPublic


class GminaPublic(GminaBase):
    id: int


class GminaPublicWithPowiat(GminaPublic):
    powiat: PowiatPublicWithWojewodztwo


class MiejscowoscPublic(MiejscowoscBase):
    id: int


class MiejscowoscPublicWithGmina(MiejscowoscPublic):
    gmina: GminaPublicWithPowiat


class UlicaPublic(UlicaBase):
    id: int
