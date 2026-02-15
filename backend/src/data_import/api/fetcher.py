import asyncio
import logging
from collections.abc import AsyncIterator
from typing import final

import httpx
from pydantic import TypeAdapter, ValidationError

from src.data_import.api.exceptions import SchoolsDataError
from src.data_import.api.models import SzkolaAPIResponse
from src.data_import.config.api import TIMEOUT, APIAuthSettings, APISettings
from src.data_import.utils.api_request import api_request

logger = logging.getLogger(__name__)

school_list_adapter = TypeAdapter(list[SzkolaAPIResponse])


def get_api_auth_credentials() -> tuple[str, str]:
    try:
        settings = APIAuthSettings()  # pyright: ignore[reportCallIssue]
    except ValidationError as err:
        raise RuntimeError(
            "Missing RSPO API credentials in .env. Set RSPO_USERNAME and RSPO_PASSWORD."
        ) from err
    return settings.RSPO_USERNAME, settings.RSPO_PASSWORD


@final
class SchoolsAPIFetcher:
    def __init__(
        self,
        base_url: str = APISettings.API_SCHOOLS_URL,
        zlikwidowana: bool = False,
    ):
        self.base_url: str = base_url
        self.headers: dict[str, str] = APISettings.HEADERS
        self.concurrent_requests: int = max(1, APISettings.CONCURRENT_REQUESTS)
        self.username, self.password = get_api_auth_credentials()
        self.zlikwidowana: bool = zlikwidowana

    async def fetch_schools_batches(
        self,
        start_page: int,
    ) -> AsyncIterator[list[SzkolaAPIResponse]]:
        current_page = start_page
        limits = httpx.Limits(
            max_connections=self.concurrent_requests,
            max_keepalive_connections=self.concurrent_requests,
        )
        request_timeout = httpx.Timeout(TIMEOUT.CONNECT, read=TIMEOUT.READ)

        async with httpx.AsyncClient(
            auth=(self.username, self.password),
            headers=self.headers,
            limits=limits,
            timeout=request_timeout,
        ) as client:
            while current_page:
                schools_data, next_page = await self._fetch_schools_segment(
                    start_page=current_page,
                    client=client,
                )

                if not schools_data:
                    return

                yield schools_data
                current_page = next_page

    async def _fetch_schools_segment(
        self,
        start_page: int,
        client: httpx.AsyncClient,
    ) -> tuple[list[SzkolaAPIResponse], int | None]:
        pages = list(range(start_page, start_page + self.concurrent_requests))

        try:
            async with asyncio.TaskGroup() as task_group:
                tasks = [
                    task_group.create_task(
                        self._fetch_schools_page(page=page, client=client)
                    )
                    for page in pages
                ]
        except* SchoolsDataError as exc_group:
            first_error = exc_group.exceptions[0]
            raise first_error from first_error
        except* Exception as exc_group:
            first_error = exc_group.exceptions[0]
            raise SchoolsDataError(
                f"Failed fetching pages {pages[0]}-{pages[-1]}: {first_error}",
                page=start_page,
            ) from first_error

        schools: list[SzkolaAPIResponse] = []

        for page, task in zip(pages, tasks, strict=True):
            result = task.result()
            if not result:
                logger.info(f"ℹ️ No schools found on page {page}")  # noqa: RUF001
                logger.info(
                    f"🏁 Finished fetching segment. Total schools in segment: {len(schools)}"
                )
                return schools, None

            schools.extend(result)
            logger.info(f"📋 Fetched {len(result)} schools from page {page}")

        logger.info(
            f"🏁 Finished fetching segment. Total schools in segment: {len(schools)}"
        )
        return schools, start_page + self.concurrent_requests

    async def _fetch_schools_page(
        self,
        page: int,
        client: httpx.AsyncClient,
    ) -> list[SzkolaAPIResponse]:
        params: dict[str, object] = {"page": page, "zlikwidowana": self.zlikwidowana}

        try:
            data = await api_request(url=self.base_url, params=params, client=client)
            return school_list_adapter.validate_python(data)
        except ValidationError as err:
            raise SchoolsDataError(
                f"Invalid API response schema on page {page}: {err}",
                page=page,
            ) from err
