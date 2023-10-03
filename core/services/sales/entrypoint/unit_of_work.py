"""
"Unit of work" is an abstraction that achieves the following:
-   Holds references to all relevant repositories for the services.
-   Allows us to execute atomic transactions.
"""

from abc import ABC

from database.db_pool import DBPoolFactory
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from services.sales.adapters import repository as repo


class AbstractUnitOfWork(ABC):
    sales: repo.AbstractSalesRepo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self, *args, **kwargs):
        return self


DEFAULT_DB_POOL_FACTORY = DBPoolFactory()


class DBPoolUnitOfWork(AbstractUnitOfWork):
    def __init__(self, db_pool_factory: DBPoolFactory = DEFAULT_DB_POOL_FACTORY):
        self.db_pool_factory = db_pool_factory

    def __enter__(self) -> "DBPoolUnitOfWork":
        self.db_pool = self.db_pool_factory.build(ISOLATION_LEVEL_READ_COMMITTED)

        self.sales = repo.SalesRepo(self.db_pool)

        return self

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.db_pool.__exit__(*args)


class FakeUnitOfWork(AbstractUnitOfWork):
    sales: repo.FakeSalesRepo

    def __init__(self) -> None:
        super().__init__()
        self.sales = repo.FakeSalesRepo()
