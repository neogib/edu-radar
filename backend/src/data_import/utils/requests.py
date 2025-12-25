import logging
import time

import requests

from src.data_import.api.exceptions import APIRequestError
from src.data_import.api.types import BasicValue
from src.data_import.core.config import TIMEOUT, RetrySettings

logger = logging.getLogger(__name__)


def api_request(
    url: str,
    params: dict[str, BasicValue] | None = None,
    headers: dict[str, str] | None = None,
    timeout: tuple[float, float] | None = None,
    max_retries: int | None = None,
    initial_delay: float | None = None,
    max_delay: float | None = None,
) -> object:
    """
    Make an API GET request with retry logic and exponential backoff.

    Args:
        url: The URL to request
        params: Query parameters
        headers: Request headers
        timeout: Tuple of (connect_timeout, read_timeout)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds

    Returns:
        JSON response from the API

    Raises:
        APIRequestError: If all retry attempts fail
    """
    # Use defaults from config if not provided
    timeout = timeout or (TIMEOUT.CONNECT, TIMEOUT.READ)
    max_retries = max_retries or RetrySettings.MAX_RETRIES
    initial_delay = initial_delay or RetrySettings.INITIAL_DELAY
    max_delay = max_delay or RetrySettings.MAX_DELAY

    delay = initial_delay

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()  # pyright: ignore[reportAny]
        except requests.exceptions.RequestException as err:
            logger.error(
                f"❌ API Request failed (attempt {attempt + 1}/{max_retries}): {err}"
            )
            if (attempt + 1) < max_retries:
                logger.info(f"⏱️ Retrying in {delay} seconds...")
                time.sleep(delay)
                delay = min(delay * 2, max_delay)

    raise APIRequestError(
        f"API Request to {url} failed after all retries",
        attempts=max_retries,
    )
