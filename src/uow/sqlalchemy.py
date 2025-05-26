from typing import Optional, Type
from types import TracebackType

from src.uow.abstract import AbstractUnitOfWork
from src.infra.storage.db import get_session_factory
from src.infra.storage.repositories.sqlalchemy.product import ProductRepository
from src.infra.storage.repositories.sqlalchemy.inventory import InventoryRepository
from src.infra.storage.repositories.sqlalchemy.sales import SalesRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Concrete Unit of Work using SQLAlchemy AsyncSession.
    Implements async context management and transaction handling.
    """

    products: ProductRepository
    inventory: InventoryRepository
    sales: SalesRepository

    def __init__(self) -> None:
        self.session_factory = get_session_factory()

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.session.begin()

        self.products = ProductRepository(self.session)
        self.inventory = InventoryRepository(self.session)
        self.sales = SalesRepository(self.session)

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
        """Commit the current transaction"""
        assert self.session is not None, "Session not initialized"
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction"""
        assert self.session is not None, "Session not initialized"
        await self.session.rollback()

    async def close(self) -> None:
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
