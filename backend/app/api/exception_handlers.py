from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.exceptions import EntityNotFoundError, SchoolLocationNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        _: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SchoolLocationNotFoundError)
    async def school_location_not_found_handler(
        _: Request, exc: SchoolLocationNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
