from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlmodel import Session

from src.app.core.database import get_session
from src.app.schemas.bounding_box import BoundingBox

SessionDep = Annotated[Session, Depends(get_session)]


def parse_bbox(
    bbox: Annotated[
        str | None,
        Query(
            description="Bounding box: min_lng,min_lat,max_lng,max_lat",
            examples=["19.0,51.9,19.1,52.0"],
        ),
    ] = None,
) -> BoundingBox | None:
    """Parse and validate bbox string parameter"""
    if not bbox:
        return None
    try:
        return BoundingBox.from_string(bbox)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid bbox parameter: {e}"
        ) from e
