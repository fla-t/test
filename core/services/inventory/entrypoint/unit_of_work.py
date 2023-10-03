"""
"Unit of work" is an abstraction that achieves the following:
-   Holds references to all relevant repositories for the services.
-   Allows us to execute atomic transactions.
"""

from abc import ABC

from database.db_pool import DBPoolFactory
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from services.inventory.adapters import repository as repo


class AbstractUnitOfWork(ABC):
    inventory_logs: repo.InventoryLogsRepo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self, *args, **kwds):
        return self


class DBPoolUnitOfWork(AbstractUnitOfWork):
    def __init__(self, db_pool_factory=DBPoolFactory()):
        self.db_pool_factory = db_pool_factory

    def __enter__(self) -> "DBPoolUnitOfWork":
        self.db_pool = self.db_pool_factory.build(ISOLATION_LEVEL_READ_COMMITTED)

        self.inventory_logs = repo.InventoryLogsRepo(self.db_pool)

        return self

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.db_pool.__exit__(*args)


class FakeUnitOfWork(AbstractUnitOfWork):
    inventory_logs: repo.FakeInventoryLogsRepo

    def __init__(self) -> None:
        super().__init__()
        self.inventory_logs = repo.FakeInventoryLogsRepo()
