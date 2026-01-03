from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.core.database import create_db_and_tables
from src.app.routers import school_types, schools


@asynccontextmanager
async def on_startup(_: FastAPI):
    # Initialize database and create tables if they don't exist on start of the app
    create_db_and_tables()
    yield


app = FastAPI(lifespan=on_startup)


origins = [
    # default port for Nuxt.js
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(schools.router)
app.include_router(school_types.router)


@app.get("/test")
async def root():
    return {"message": "Backend FastAPI"}
