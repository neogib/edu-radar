from fastapi import APIRouter

from app.api.v1.endpoints import filters, school_types, schools

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(schools.router)
api_router.include_router(filters.router)
api_router.include_router(school_types.router)
