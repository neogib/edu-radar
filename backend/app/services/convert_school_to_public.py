from typing import cast

from app.models.schools import (
    Szkola,
)
from app.schemas.schools import SzkolaPublicShort


def to_public_short(
    szkola: Szkola,
    latitude: float,
    longitude: float,
) -> SzkolaPublicShort:
    return SzkolaPublicShort(
        id=cast(int, szkola.id),
        nazwa=szkola.nazwa,
        latitude=latitude,
        longitude=longitude,
        wynik=szkola.wynik,
        typ=szkola.typ.nazwa,
        status=szkola.status_publicznoprawny.nazwa,
    )
