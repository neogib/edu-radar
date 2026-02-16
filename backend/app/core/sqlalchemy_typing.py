from typing import cast

from sqlalchemy.orm import QueryableAttribute


def orm_rel_attr(attr: object) -> QueryableAttribute[object]:
    """
    Cast SQLModel relationship attributes to SQLAlchemy QueryableAttribute
    for typed loader options (joinedload/selectinload).
    """
    return cast(QueryableAttribute[object], attr)
