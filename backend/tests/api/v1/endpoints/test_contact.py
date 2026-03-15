from fastapi.testclient import TestClient

from app.api.v1.endpoints.contact import get_turnstile_service
from app.main import app
from app.services.exceptions import TurnstileVerificationFailedError


class FakeTurnstileService:
    def __init__(self) -> None:
        self.captured_token: str | None = None
        self.captured_ip: str | None = None

    async def verify_token(self, token: str, remote_ip: str | None = None) -> None:
        self.captured_token = token
        self.captured_ip = remote_ip


class FailingTurnstileService:
    async def verify_token(self, token: str, remote_ip: str | None = None) -> None:
        _ = (token, remote_ip)
        raise TurnstileVerificationFailedError(error_codes=["invalid-input-response"])


def test_submit_contact_returns_success(client: TestClient) -> None:
    fake = FakeTurnstileService()
    app.dependency_overrides[get_turnstile_service] = lambda: fake
    try:
        response = client.post(
            "/api/v1/contact",
            json={
                "name": "Jan Kowalski",
                "email": "jan@example.com",
                "topic": "Pytanie",
                "message": "Prosze o kontakt.",
                "turnstile_token": "token-123",
            },
            headers={
                "cf-connecting-ip": "203.0.113.10",
                "x-forwarded-for": "198.51.100.20",
            },
        )
    finally:
        _ = app.dependency_overrides.pop(get_turnstile_service, None)

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert fake.captured_token == "token-123"
    assert fake.captured_ip == "203.0.113.10"


def test_submit_contact_returns_400_when_turnstile_verification_fails(
    client: TestClient,
) -> None:
    fake = FailingTurnstileService()
    app.dependency_overrides[get_turnstile_service] = lambda: fake
    try:
        response = client.post(
            "/api/v1/contact",
            json={
                "name": "Jan Kowalski",
                "email": "jan@example.com",
                "topic": "Pytanie",
                "message": "Prosze o kontakt.",
                "turnstile_token": "token-123",
            },
        )
    finally:
        _ = app.dependency_overrides.pop(get_turnstile_service, None)

    assert response.status_code == 400
    assert response.json()["detail"] == "Turnstile verification failed."
    assert response.json()["errorCodes"] == ["invalid-input-response"]


def test_submit_contact_returns_422_for_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jan Kowalski",
            "email": "not-email",
            "topic": "",
            "message": "",
            "turnstile_token": "",
        },
    )
    assert response.status_code == 422
