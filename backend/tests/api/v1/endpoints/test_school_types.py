from typing import TypedDict

from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app.schemas.schools import TypSzkolyPublic


class ErrorResponse(TypedDict):
    detail: str


school_type_adapter = TypeAdapter(TypSzkolyPublic)
school_type_list_adapter = TypeAdapter(list[TypSzkolyPublic])
error_response_adapter = TypeAdapter(ErrorResponse)


def test_read_school_types_returns_seeded_data(seeded_client: TestClient) -> None:
    response = seeded_client.get("/api/v1/school_types/")
    assert response.status_code == 200

    data = school_type_list_adapter.validate_python(response.json())

    assert all(item.nazwa for item in data)


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
    school_type_name = all_data[0].nazwa

    response = seeded_client.get(f"/api/v1/school_types/{school_type_id}")
    assert response.status_code == 200
    data = school_type_adapter.validate_python(response.json())

    assert data.id == school_type_id
    assert data.nazwa == school_type_name


def test_read_school_type_returns_404_for_missing_id(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.get("/api/v1/school_types/999999")
    assert response.status_code == 404
    data = error_response_adapter.validate_python(response.json())

    assert data["detail"] == "TypSzkoly with id=999999 not found"
