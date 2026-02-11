from types import TracebackType
from typing import Self

from sqlalchemy import BinaryExpression, Engine
from sqlmodel import Session, SQLModel, select

from src.app.core.database import engine


class DatabaseManagerBase:
    """Base class providing session management functionality"""

    _engine: Engine
    _session: Session | None
    _owns_session: bool

    def __init__(self, session: Session | None = None):
        self._engine = engine
        self._session = session
        self._owns_session = session is None

    def __enter__(self) -> Self:
        # Create a session only when one was not injected from outside.
        if self._session is None:
            self._session = Session(self._engine)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Close the session when exiting the context
        self.close()

    def close(self) -> None:
        """Manual close method for when not using as context manager"""
        if self._session:
            if self._owns_session:
                self._session.close()
            self._session = None

    def _ensure_session(self) -> Session:
        """Ensure we have an active session and return it"""
        if self._session is None:
            self._session = Session(self._engine)
        return self._session

    def _select_where[T: SQLModel](
        self, model: type[T], condition: BinaryExpression[bool] | bool
    ) -> T | None:
        """Generic method to select a record based on a condition"""
        session = self._ensure_session()
        return session.exec(select(model).where(condition)).first()
