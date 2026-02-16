import asyncio
import logging

import httpx

from app.data_import.api.exceptions import APIRequestError
from app.data_import.config.api import RetrySettings

logger = logging.getLogger(__name__)


async def api_request(
    url: str,
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    max_retries: int = RetrySettings.MAX_RETRIES,
    initial_delay: float = RetrySettings.INITIAL_DELAY,
    max_delay: float = RetrySettings.MAX_DELAY,
    client: httpx.AsyncClient | None = None,
) -> object:
    """
    Make an API GET request with retry logic and exponential backoff.

    Args:
        url: The URL to request
        params: Query parameters
        headers: Request headers
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds

    Returns:
        JSON response from the API

    Raises:
        APIRequestError: If all retry attempts fail
    """
    delay = initial_delay

    owns_client = client is None
    request_client = client if client is not None else httpx.AsyncClient()
    try:
        for attempt in range(max_retries):
            try:
                response = await request_client.get(
                    url,
                    headers=headers,
                    params=params,  # pyright: ignore[reportArgumentType]
                )
                _ = response.raise_for_status()
            except httpx.HTTPError as err:
                logger.error(
                    f"❌ API Request failed (attempt {attempt + 1}/{max_retries}): {err}"
                )
                if (attempt + 1) < max_retries:
                    logger.info(f"⏱️ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
                continue
            try:
                return response.json()  # pyright: ignore[reportAny]
            except ValueError:  # api doesn't reponse with json
                return response.text
    finally:
        if owns_client:
            await request_client.aclose()

    raise APIRequestError(
        f"API Request to {url} failed after all retries",
        attempts=max_retries,
    )
