import asyncio
import logging
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.turnstile import TurnstileConfig
from app.services.exceptions import (
    TurnstileServiceUnavailableError,
    TurnstileVerificationFailedError,
)

logger = logging.getLogger(__name__)


class TurnstileVerifyResponse(BaseModel):
    success: bool
    error_codes: list[str] = Field(default_factory=list, alias="error-codes")


class TurnstileService:
    verification_url: str = TurnstileConfig.VERIFICATION_URL
    max_attempts: int = TurnstileConfig.MAX_ATTEMPTS
    backoff_seconds: tuple[float, ...] = TurnstileConfig.BACKOFF_SECONDS
    request_timeout_seconds: float = TurnstileConfig.REQUEST_TIMEOUT_SECONDS

    def __init__(self) -> None:
        self.settings: Settings = Settings()  # pyright: ignore[reportCallIssue]

    async def verify_token(self, token: str, remote_ip: str | None = None) -> None:
        secret_key = self.settings.TURNSTILE_SECRET_KEY
        if not secret_key:
            raise TurnstileServiceUnavailableError(
                "TURNSTILE_SECRET_KEY is not configured"
            )

        idempotency_key = str(uuid4())
        payload: dict[str, str] = {
            "secret": secret_key,
            "response": token,
            "idempotency_key": idempotency_key,
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        async with httpx.AsyncClient(timeout=self.request_timeout_seconds) as client:
            for attempt in range(1, self.max_attempts + 1):
                try:
                    response = await client.post(self.verification_url, data=payload)
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt < self.max_attempts:
                        await asyncio.sleep(self._get_backoff_delay(attempt))
                        continue
                    raise TurnstileServiceUnavailableError(
                        "Could not verify Turnstile token"
                    ) from exc

                if 500 <= response.status_code <= 599:
                    if attempt < self.max_attempts:
                        await asyncio.sleep(self._get_backoff_delay(attempt))
                        continue
                    raise TurnstileServiceUnavailableError(
                        "Turnstile verification service returned server error"
                    )

                if not 200 <= response.status_code <= 299:
                    raise TurnstileServiceUnavailableError(
                        f"Turnstile verification failed with status {response.status_code}"
                    )

                try:
                    verification = TurnstileVerifyResponse.model_validate(
                        response.json()
                    )
                except ValueError as exc:
                    raise TurnstileServiceUnavailableError(
                        "Invalid Turnstile response payload"
                    ) from exc
                if not verification.success:
                    logger.warning(
                        "Turnstile verification failed with error codes: %s",
                        verification.error_codes,
                    )
                    raise TurnstileVerificationFailedError(
                        error_codes=verification.error_codes
                    )
                logger.info("Turnstile verification succeeded")
                return

        raise TurnstileServiceUnavailableError("Could not verify Turnstile token")

    def _get_backoff_delay(self, attempt: int) -> float:
        if attempt <= len(self.backoff_seconds):
            return self.backoff_seconds[attempt - 1]
        return self.backoff_seconds[-1]
