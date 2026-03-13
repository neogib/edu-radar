from typing import TypedDict

import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app.schemas.schools import TypSzkolyPublic
from app.services.exceptions import EntityNotFoundError

pytestmark = pytest.mark.seeded


class ErrorResponse(TypedDict):
    detail: str


school_type_adapter = TypeAdapter(TypSzkolyPublic)
school_type_list_adapter = TypeAdapter(list[TypSzkolyPublic])
error_response_adapter = TypeAdapter(ErrorResponse)


def test_read_school_types_returns_seeded_data(seeded_client: TestClient) -> None:
    response = seeded_client.get("/api/v1/school_types/")
    assert response.status_code == 200

    data = school_type_list_adapter.validate_python(response.json())

    assert len(data) > 0


def test_read_school_types_accepts_repeated_names_query_param(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.get(
        "/api/v1/school_types/",
        params=[("names", "___missing_name_1___"), ("names", "___missing_name_2___")],
    )
    assert response.status_code == 200
    data = school_type_list_adapter.validate_python(response.json())
    assert data == []


def test_read_school_types_filters_by_existing_name(seeded_client: TestClient) -> None:
    all_response = seeded_client.get("/api/v1/school_types/")
    assert all_response.status_code == 200

    all_data = school_type_list_adapter.validate_python(all_response.json())
    assert len(all_data) > 0
    existing_name = all_data[0].nazwa

    response = seeded_client.get(
        "/api/v1/school_types/",
        params=[("names", existing_name)],
    )
    assert response.status_code == 200
    data = school_type_list_adapter.validate_python(response.json())

    assert len(data) > 0
    assert all(item.nazwa == existing_name for item in data)


def test_read_school_type_by_existing_id(seeded_client: TestClient) -> None:
    all_response = seeded_client.get("/api/v1/school_types/")
    assert all_response.status_code == 200

    all_data = school_type_list_adapter.validate_python(all_response.json())
    assert len(all_data) > 0

    school_type_id = all_data[0].id

    response = seeded_client.get(f"/api/v1/school_types/{school_type_id}")
    assert response.status_code == 200
    data = school_type_adapter.validate_python(response.json())

    assert data.id == school_type_id


def test_read_school_type_returns_404_for_missing_id(
    seeded_client: TestClient,
) -> None:
    all_response = seeded_client.get("/api/v1/school_types/")
    assert all_response.status_code == 200
    all_data = school_type_list_adapter.validate_python(all_response.json())
    assert len(all_data) > 0
    missing_school_type_id = max(school_type.id for school_type in all_data) + 1

    response = seeded_client.get(f"/api/v1/school_types/{missing_school_type_id}")
    assert response.status_code == 404
    data = error_response_adapter.validate_python(response.json())

    expected_error = EntityNotFoundError(
        entity_id=missing_school_type_id, model_name="TypSzkoly"
    )
    assert data["detail"] == str(expected_error)
