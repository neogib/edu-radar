"""Shared backend test fixtures."""

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Connection, Transaction, event
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from alembic import command
from app.core.database import get_session
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]


class TestSettings(BaseSettings):
    TEST_DATABASE_URI: PostgresDsn

    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file=BACKEND_DIR / ".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_test_connection_string() -> str:
    return str(TestSettings().TEST_DATABASE_URI)  # pyright: ignore[reportCallIssue]


@pytest.fixture(scope="session")
def migrated_test_db() -> Generator[None]:
    # This applies all Alembic migrations before any tests start.
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", get_test_connection_string())
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture(scope="session")
def engine(
    migrated_test_db: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> Generator[Engine]:
    # Fixture dependency order:
    # seeded_client -> seeded_session -> engine -> migrated_test_db
    # client -> session -> engine -> migrated_test_db
    # Adding `migrated_test_db` here guarantees migrations are applied first.
    yield create_engine(get_test_connection_string())


@pytest.fixture
def seeded_session(engine: Engine) -> Generator[Session]:
    # Read-oriented tests use existing imported/seeded data without cleanup.
    with Session(engine) as session:
        yield session


def _test_client_for_session(session: Session) -> Generator[TestClient]:
    def get_session_override() -> Generator[Session]:
        yield session

    app.dependency_overrides[get_session] = get_session_override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def seeded_client(seeded_session: Session) -> Generator[TestClient]:
    yield from _test_client_for_session(seeded_session)


@pytest.fixture
def session(engine: Engine) -> Generator[Session]:
    # Write-oriented tests run in an isolated transaction.
    # Endpoint-level `session.commit()` persists only inside this test and is rolled back.
    connection: Connection = engine.connect()
    outer_transaction: Transaction = connection.begin()
    test_session = Session(bind=connection)
    savepoint: Transaction = connection.begin_nested()

    @event.listens_for(test_session, "after_transaction_end")
    def restart_savepoint(_session: Session, transaction: object) -> None:
        nonlocal savepoint
        parent = getattr(transaction, "parent", None)
        is_nested = bool(getattr(transaction, "nested", False))
        if is_nested and parent is not None and not savepoint.is_active:
            savepoint = connection.begin_nested()

    try:
        yield test_session
    finally:
        test_session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    yield from _test_client_for_session(session)
