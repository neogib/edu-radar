from datetime import date, datetime
from typing import cast

from pydantic import ConfigDict, field_validator, model_validator
from sqlmodel import SQLModel

from src.app.models.schools import (
    EtapEdukacjiBase,
    KategoriaUczniowBase,
    StatusPublicznoprawnyBase,
    SzkolaExtendedData,
    TypSzkolyBase,
)
from src.data_import.utils.convert_to_camel import custom_camel


class GeolocationAPIResponse(SQLModel):
    latitude: float
    longitude: float


class SzkolaAPIResponse(SzkolaExtendedData):
    model_config: ConfigDict = ConfigDict(alias_generator=custom_camel)  # pyright: ignore[reportIncompatibleVariableOverride]
    geolokalizacja: GeolocationAPIResponse
    typ: TypSzkolyBase
    status_publiczno_prawny: StatusPublicznoprawnyBase
    etapy_edukacji: list[EtapEdukacjiBase] | None
    wojewodztwo: str
    wojewodztwo_kod_TERYT: str  # noqa: N815
    powiat: str
    powiat_kod_TERYT: str  # noqa: N815
    gmina: str
    gmina_kod_TERYT: str  # noqa: N815
    miejscowosc: str
    miejscowosc_kod_TERYT: str  # noqa: N815
    ulica: str | None
    ulica_kod_TERYT: str | None  # noqa: N815
    ksztalcenie_zawodowe: dict[str, str] | None
    kategoria_uczniow: KategoriaUczniowBase

    @model_validator(mode="before")
    @classmethod
    def empty_str_list_to_none[T](cls, data: T) -> T:
        """Convert empty strings and empty lists to None for all fields."""
        if not isinstance(data, dict):
            raise ValueError(f"Expected data to be a dictionary, but got {data}")

        # Convert empty strings to None for all fields
        for field_name, field_value in list(cast(dict[str, object], data).items()):
            if (
                field_value == "" or field_value == []
            ):  # "" or [] are considered empty, 0 is a normal value
                data[field_name] = None

        return cast(T, data)

    @field_validator(
        "data_zalozenia",
        "data_rozpoczecia",
        "data_likwidacji",
        mode="before",
    )
    @classmethod
    def parse_datetime_to_date(cls, v: object):
        if v is None:
            return None

        if isinstance(v, datetime):
            return v.date()

        if isinstance(v, date):
            return v

        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v).date()
            except ValueError as e:
                raise ValueError(f"Invalid ISO datetime/date string: {v}") from e

        raise TypeError(
            f"Expected date, datetime, ISO string, or None; got {type(v).__name__}"
        )
