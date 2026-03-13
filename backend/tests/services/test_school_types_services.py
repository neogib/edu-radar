import pytest
from sqlmodel import Session

from app.services.exceptions import EntityNotFoundError
from app.services.school_type_service import SchoolTypeService

pytestmark = pytest.mark.seeded


def test_get_all_school_types(seeded_session: Session) -> None:
    service = SchoolTypeService(seeded_session)
    school_types = service.get_school_types()

    assert len(school_types) > 0


def test_get_school_types_by_existing_names(seeded_session: Session) -> None:
    service = SchoolTypeService(seeded_session)
    all_school_types = service.get_school_types()
    assert len(all_school_types) > 0

    unique_existing_names = list(
        {school_type.nazwa for school_type in all_school_types}
    )
    existing_names = unique_existing_names[:2]
    query_names = [*existing_names, "__missing_school_type_name__", existing_names[0]]
    school_types = service.get_school_types_by_names(query_names)

    expected_ids = {
        school_type.id
        for school_type in all_school_types
        if school_type.nazwa in existing_names
    }
    actual_ids = {school_type.id for school_type in school_types}

    assert None not in expected_ids
    assert None not in actual_ids
    assert actual_ids == expected_ids


def test_get_school_types_by_empty_names_returns_empty_list(
    seeded_session: Session,
) -> None:
    service = SchoolTypeService(seeded_session)
    school_types = service.get_school_types_by_names([])
    assert school_types == []


def test_get_school_type_by_existing_id(seeded_session: Session) -> None:
    service = SchoolTypeService(seeded_session)
    all_school_types = service.get_school_types()
    assert len(all_school_types) > 0

    school_type_id = all_school_types[0].id
    assert school_type_id is not None

    school_type_name = all_school_types[0].nazwa
    assert school_type_name is not None

    school_type = service.get_school_type(school_type_id)
    assert school_type.id == school_type_id
    assert school_type.nazwa == school_type_name


def test_get_school_type_returns_not_found_for_missing_id(
    seeded_session: Session,
) -> None:
    service = SchoolTypeService(seeded_session)
    all_school_types = service.get_school_types()
    assert len(all_school_types) > 0
    existing_ids = [
        school_type_id
        for school_type in all_school_types
        if (school_type_id := school_type.id) is not None
    ]
    assert len(existing_ids) == len(all_school_types)
    missing_id = max(existing_ids) + 1
    with pytest.raises(EntityNotFoundError):
        _ = service.get_school_type(missing_id)
