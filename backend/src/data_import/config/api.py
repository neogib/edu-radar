from pathlib import Path
from typing import ClassVar, final

from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class APISettings:
    API_SCHOOLS_URL: str = "https://api.rspo.gov.pl/api/placowki/"
    HEADERS: ClassVar[dict[str, str]] = {"accept": "application/json"}
    START_PAGE: int = 1
    CONCURRENT_REQUESTS: int = 10


class APIAuthSettings(BaseSettings):
    RSPO_USERNAME: str
    RSPO_PASSWORD: str

    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@final
class RetrySettings:
    INITIAL_DELAY = 1
    MAX_DELAY = 30
    MAX_RETRIES = 20


@final
class TIMEOUT:
    CONNECT = 30
    READ = 90
