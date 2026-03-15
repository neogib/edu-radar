import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app.schemas.schools import SzkolaPublicShort, SzkolaPublicWithRelations
from tests.constants import MISSING_INT_ID

pytestmark = pytest.mark.seeded

school_short_list_adapter = TypeAdapter(list[SzkolaPublicShort])
SCHOOLS_LIVE_TEST_LIMIT = 10


def test_read_schools_live_returns_seeded_data(seeded_client: TestClient) -> None:
    response = seeded_client.get(
        "/api/v1/schools/live",
        params={"limit": SCHOOLS_LIVE_TEST_LIMIT},
    )
    assert response.status_code == 200

    data = school_short_list_adapter.validate_python(response.json())
    assert 0 < len(data) <= SCHOOLS_LIVE_TEST_LIMIT


def test_read_schools_live_returns_422_for_invalid_query(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.get("/api/v1/schools/live", params={"q": "x"})
    assert response.status_code == 422


def test_read_school_returns_response_model(seeded_client: TestClient) -> None:
    schools_response = seeded_client.get(
        "/api/v1/schools/live",
        params={"limit": SCHOOLS_LIVE_TEST_LIMIT},
    )
    assert schools_response.status_code == 200
    schools = school_short_list_adapter.validate_python(schools_response.json())
    assert len(schools) > 0

    school_id = schools[0].id
    response = seeded_client.get(f"/api/v1/schools/{school_id}")
    assert response.status_code == 200

    data = SzkolaPublicWithRelations.model_validate(response.json())
    assert data.id == school_id


def test_read_school_returns_404_for_missing_id(seeded_client: TestClient) -> None:
    response = seeded_client.get(f"/api/v1/schools/{MISSING_INT_ID}")
    assert response.status_code == 404
