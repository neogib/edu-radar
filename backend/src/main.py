from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.routers import filters, school_types, schools

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(schools.router)
app.include_router(school_types.router)
app.include_router(filters.router)


@app.get("/test")
async def root():
    return {"message": "Backend FastAPI"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
