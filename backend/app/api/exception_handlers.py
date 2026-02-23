import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.exceptions import (
    EntityNotFoundError,
    SchoolLocationNotFoundError,
    TurnstileServiceUnavailableError,
    TurnstileVerificationFailedError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        _: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(SchoolLocationNotFoundError)
    async def school_location_not_found_handler(
        _: Request, exc: SchoolLocationNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(TurnstileVerificationFailedError)
    async def turnstile_verification_failed_handler(
        _: Request, exc: TurnstileVerificationFailedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Turnstile verification failed.",
                "errorCodes": exc.error_codes,
            },
        )

    @app.exception_handler(TurnstileServiceUnavailableError)
    async def turnstile_service_unavailable_handler(
        _: Request, exc: TurnstileServiceUnavailableError
    ) -> JSONResponse:
        logger.exception("Turnstile verification service unavailable", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Turnstile verification service is unavailable."},
        )
