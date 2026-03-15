import pytest
from fastapi.testclient import TestClient

from app.schemas.ranking import RankingsFiltersResponse, RankingsResponse

pytestmark = pytest.mark.seeded


def test_read_rankings_filters_returns_seeded_data(seeded_client: TestClient) -> None:
    response = seeded_client.get("/api/v1/rankings/filters")
    assert response.status_code == 200

    data = RankingsFiltersResponse.model_validate(response.json())
    assert len(data.years) > 0
    assert len(data.scopes) > 0
    assert len(data.types) > 0
    assert len(data.directions) > 0
    assert len(data.voivodeships) > 0
    assert len(data.counties) > 0
    assert len(data.statuses) > 0


def test_read_rankings_returns_response_model(seeded_client: TestClient) -> None:
    filters_response = seeded_client.get("/api/v1/rankings/filters")
    assert filters_response.status_code == 200
    filters_data = RankingsFiltersResponse.model_validate(filters_response.json())
    assert len(filters_data.years) > 0

    response = seeded_client.get(
        "/api/v1/rankings/",
        params={
            "year": filters_data.years[0],
            "type": "E8",
            "scope": "KRAJ",
            "direction": "BEST",
        },
    )
    assert response.status_code == 200

    data = RankingsResponse.model_validate(response.json())
    assert data.page >= 1
    assert data.total >= 0


def test_read_rankings_returns_422_for_missing_voivodeship_id_when_scope_is_wojewodztwo(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.get(
        "/api/v1/rankings/",
        params={
            "year": 2024,
            "type": "E8",
            "scope": "WOJEWODZTWO",
            "direction": "BEST",
        },
    )
    assert response.status_code == 422
