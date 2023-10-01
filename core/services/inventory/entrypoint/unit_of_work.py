"""
"Unit of work" is an abstraction that achieves the following:
-   Holds references to all relevant repositories for the services.
-   Allows us to execute atomic transactions.
"""

from abc import ABC

from database.db_pool import DBPool, DBPoolFactory
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from services.inventory.adapters import repository as repo


class AbstractUnitOfWork(ABC):
    skus: repo.AbstractSKURepo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


DEFAULT_DB_POOL_FACTORY = DBPoolFactory()


class DBPoolUnitOFWork(AbstractUnitOfWork):
    def __init__(self, db_pool_factory: DBPoolFactory = DEFAULT_DB_POOL_FACTORY):
        self.db_pool_factory = DBPoolFactory()

    def __enter__(self):
        self.db_pool = self.db_pool_factory.build(ISOLATION_LEVEL_READ_COMMITTED)
        self.skus = repo.SKURepo(self.db_pool)

        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.db_pool.__exit__(*args)


class FakeUnitOfWork(AbstractUnitOfWork):
    skus: repo.FakeSKURepo

    def __init__(self):
        super().__init__()
        self.skus = repo.FakeSKURepo()
