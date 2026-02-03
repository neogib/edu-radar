import logging
from typing import cast

from src.data_import.api.exceptions import APIRequestError, SchoolsDataError
from src.data_import.config.api import APISettings
from src.data_import.utils.api_request import api_request

logger = logging.getLogger(__name__)


class HydraResponse:
    """
    Facilitate working with Hydra Web API responses
    """

    def __init__(self, response_json: dict[str, object]):
        self.raw: dict[str, object] = response_json

    @property
    def items(self) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], self.raw.get("hydra:member", []))

    @property
    def next_page_url(self) -> str | None:
        view = cast(dict[str, str], self.raw.get("hydra:view", {}))
        return view.get("hydra:next")


class SchoolsAPIFetcher:
    def __init__(
        self,
        base_url: str = APISettings.API_SCHOOLS_URL,
        headers: dict[str, str] = APISettings.HEADERS,
    ):
        self.base_url: str = base_url
        self.headers: dict[str, str] = headers

    def fetch_schools_page(self, page: int = 1) -> HydraResponse:
        """
        Fetch schools data from one page
        """
        params: dict[str, object] = {"page": page}

        try:
            data = cast(
                dict[str, object],
                api_request(
                    url=self.base_url,
                    params=params,
                    headers=self.headers,
                ),
            )
            hydra_response = HydraResponse(data)
            return hydra_response
        except APIRequestError as err:
            logging.critical(f"🚫 Fatal error fetching schools data: {err}")
            raise SchoolsDataError(str(err), page=page) from err

    def fetch_schools_segment(
        self, start_page: int, max_schools: int = APISettings.MAX_SCHOOLS_SEGMENT
    ) -> tuple[list[dict[str, object]], int | None]:
        """
        Fetch a segment of schools data, up to max_schools.

        Returns:
            Tuple of (schools_list, next_page_number)
        """
        schools: list[dict[str, object]] = []
        current_page = start_page

        while current_page and len(schools) < max_schools:
            response = self.fetch_schools_page(page=current_page)

            # extract schools from response
            if response.items:
                new_schools = response.items
                schools.extend(new_schools)
                logger.info(
                    f"📋 Fetched {len(new_schools)} schools from page {current_page}"
                )
            else:
                logger.info(f"ℹ️ No schools found on page {current_page}")  # noqa: RUF001

            # check if page limit is reached
            if APISettings.PAGE_LIMIT and current_page >= APISettings.PAGE_LIMIT:
                current_page = None
                break

            if response.next_page_url:  # check if there are more pages in reponse
                current_page += 1
            else:  # no more pages - stopping...
                current_page = None

        logger.info(
            f"🏁 Finished fetching segment. Total schools in segment: {len(schools)}"
        )
        return schools, current_page
