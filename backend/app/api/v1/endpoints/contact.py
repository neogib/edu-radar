import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.schemas.contact import ContactSubmitRequest, ContactSubmitResponse
from app.services.turnstile_service import TurnstileService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/contact",
    tags=["contact"],
)


def get_turnstile_service() -> TurnstileService:
    return TurnstileService()


TurnstileServiceDep = Annotated[TurnstileService, Depends(get_turnstile_service)]


def get_client_ip(request: Request) -> str | None:
    if cf_connecting_ip := request.headers.get("cf-connecting-ip"):
        logger.info(f"Client IP from cf-connecting-ip: {cf_connecting_ip}")
        return cf_connecting_ip.strip()

    if forwarded_for := request.headers.get("x-forwarded-for"):
        logger.info(f"Client IP from x-forwarded-for: {forwarded_for}")
        return forwarded_for.split(",", maxsplit=1)[0].strip()

    if request.client:
        logger.info(f"Client IP from request.client: {request.client.host}")
        return request.client.host

    logger.info("Could not determine client IP from request")
    return None


@router.post("", status_code=status.HTTP_200_OK)
async def submit_contact(
    payload: ContactSubmitRequest,
    request: Request,
    turnstile_service: TurnstileServiceDep,
) -> ContactSubmitResponse:
    client_ip = get_client_ip(request)

    await turnstile_service.verify_token(
        token=payload.turnstile_token, remote_ip=client_ip
    )

    return ContactSubmitResponse(success=True)
