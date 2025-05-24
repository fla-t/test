from typing import Optional, Type
from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.uow.abstract import AbstractUnitOfWork
from src.infra.storage.db import session_factory


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Concrete Unit of Work using SQLAlchemy AsyncSession.
    Implements async context management and transaction handling.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = session_factory,
    ) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] = session_factory
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.close()

    async def commit(self) -> None:
        """Commit the current transaction."""
        assert self.session is not None, "Session not initialized"
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        assert self.session is not None, "Session not initialized"
        await self.session.rollback()

    async def close(self) -> None:
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
