from typing import Optional, Type
from types import TracebackType

from src.uow.abstract import AbstractUnitOfWork
from src.infra.storage.repositories.product import ProductRepository
from src.infra.storage.repositories.inventory import InventoryRepository
from src.infra.storage.repositories.sales import SalesRepository


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """
    Concrete Unit of Work using SQLAlchemy AsyncSession.
    Implements async context management and transaction handling.
    """

    products: ProductRepository
    inventory: InventoryRepository
    sales: SalesRepository

    async def __aenter__(self) -> "InMemoryUnitOfWork":
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
        pass

    async def rollback(self) -> None:
        pass

    async def close(self) -> None:
        pass
