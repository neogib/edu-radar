from src.app.models.locations import (
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


class GminaPublic(GminaBase):
    id: int


class MiejscowoscPublic(MiejscowoscBase):
    id: int


class UlicaPublic(UlicaBase):
    id: int
