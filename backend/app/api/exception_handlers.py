from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.exceptions import SchoolLocationNotFoundError, SchoolNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SchoolNotFoundError)
    async def school_not_found_handler(
        _: Request, exc: SchoolNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SchoolLocationNotFoundError)
    async def school_location_not_found_handler(
        _: Request, exc: SchoolLocationNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
