from typing import Optional

from database.db import BaseDatabase
from database.pooler import ConnectionPooler, Pool
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, connection


class DBPool(BaseDatabase):
    """
    Handler for postgres queries managed by connection pooling
    inits DB connection pool upon creation

    """

    def __init__(
        self, isolation_level=ISOLATION_LEVEL_READ_COMMITTED, db_pool_name="default"
    ) -> None:
        super().__init__()
        self._pool: Optional[Pool] = ConnectionPooler.get_pool(db_pool_name)
        self._conn: Optional[connection] = self._pool.get_conn()
        self._conn.set_session(isolation_level=isolation_level)

    def close(self) -> None:
        """Close connection"""
        self._pool.put_conn(self._conn)
        self._pool = None
        self._conn = None


class DBPoolFactory:
    @staticmethod
    def build(isolation_level: int = ISOLATION_LEVEL_READ_COMMITTED) -> DBPool:
        return DBPool(isolation_level=isolation_level)
