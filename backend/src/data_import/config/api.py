from typing import ClassVar, final


@final
class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/?zlikwidowana=true"
    HEADERS: ClassVar[dict[str, str]] = {"accept": "application/ld+json"}
    START_PAGE: int = 201
    PAGE_LIMIT: int | None = None  # the last page to fetch, if None there is no limit
    MAX_SCHOOLS_SEGMENT: int = 500


@final
class RetrySettings:
    INITIAL_DELAY: int = 1
    MAX_DELAY: int = 30
    MAX_RETRIES: int = 20


@final
class TIMEOUT:
    CONNECT: int = 30
    READ: int = 90
