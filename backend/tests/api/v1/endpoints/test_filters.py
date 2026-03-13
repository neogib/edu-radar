from fastapi.testclient import TestClient

from app.schemas.school_filters import SchoolFiltersResponse


def test_read_filters_returns_seeded_data(seeded_client: TestClient) -> None:
    response = seeded_client.get("/api/v1/filters")
    assert response.status_code == 200

    data = SchoolFiltersResponse.model_validate(response.json())

    assert len(data.school_types) > 0
    assert len(data.public_statuses) > 0
    assert len(data.student_categories) > 0
    assert len(data.vocational_training) > 0
