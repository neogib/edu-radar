from fastapi import APIRouter

from app.api.v1.endpoints import contact, filters, rankings, school_types, schools

api_v1_router = APIRouter()
api_v1_router.include_router(schools.router)
api_v1_router.include_router(filters.router)
api_v1_router.include_router(school_types.router)
api_v1_router.include_router(rankings.router)
api_v1_router.include_router(contact.router)
