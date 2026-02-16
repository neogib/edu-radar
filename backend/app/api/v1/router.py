from fastapi import APIRouter

from app.api.v1.endpoints import filters, school_types, schools

api_v1_router = APIRouter()
api_v1_router.include_router(schools.router)
api_v1_router.include_router(filters.router)
api_v1_router.include_router(school_types.router)
