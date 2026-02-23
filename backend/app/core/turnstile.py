from typing import final


@final
class TurnstileConfig:
    VERIFICATION_URL: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    REQUEST_TIMEOUT_SECONDS: float = 10.0
    MAX_ATTEMPTS: int = 3
    BACKOFF_SECONDS: tuple[float, ...] = (0.2, 0.5)
