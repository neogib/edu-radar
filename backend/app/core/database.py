from sqlmodel import Session, create_engine

from app.core.config import Settings

# DATABASE_URI is of type PostgresDsn, that's why we need get_connection_string method
settings = Settings()  # pyright: ignore[reportCallIssue]
engine = create_engine(settings.get_connection_string())


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
