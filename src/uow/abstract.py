from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar
from types import TracebackType

from src.domain.product.repository import AbstractProductRepository
from src.domain.inventory.repository import AbstractInventoryRepository
from src.domain.sales.repository import AbstractSalesRepository

ProductRepository = TypeVar("ProductRepository", bound=AbstractProductRepository)
InventoryRepository = TypeVar("InventoryRepository", bound=AbstractInventoryRepository)
SalesRepository = TypeVar("SalesRepository", bound=AbstractSalesRepository)


class AbstractUnitOfWork(ABC):
    """
    Defines the interface for an asynchronous Unit of Work.
    Concrete implementations must implement context management and transaction methods.
    """

    products: ProductRepository
    inventory: InventoryRepository
    sales: SalesRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        """Enter the async context and return the unit of work instance"""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context; commit if no exception, else rollback"""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Persist changes in the current transaction"""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back the current transaction"""
        raise NotImplementedError
