import atexit
import os
import threading
from typing import Dict, Optional

from psycopg2 import OperationalError
from psycopg2.extensions import connection
from psycopg2.pool import ThreadedConnectionPool

MIN_PG_CONNS = int(os.environ.get("POSTGRES_MIN_POOL_CONNS", 2))
MAX_PG_CONNS = int(os.environ.get("POSTGRES_MAX_POOL_CONNS", 5))
MAX_PG_CONNECT_RETRIES = int(os.environ.get("POSTGRES_MAX_CONN_RETRIES", 5))


class Pool:
    """Represents a psycopg2 connection pool"""

    _pool: Optional[ThreadedConnectionPool]
    _pool_lock: threading.Lock()

    def __init__(
        self, min_pg_conns: int = MIN_PG_CONNS, max_pg_conns: int = MAX_PG_CONNS, **conn_args
    ) -> None:
        self.min_pg_conns = min_pg_conns
        self.max_pg_conns = max_pg_conns
        self.conn_args = self._get_args(**conn_args)

        self._pool: Optional[ThreadedConnectionPool] = None
        self._pool_lock = threading.Lock()

    def close_all_conns(self) -> None:
        """Close all connections if there is a pool"""
        with self._pool_lock:
            if not self._pool_lock:
                return
            if self._pool:
                self._pool.closeall()
                self._pool = None

    def get_pool(self) -> ThreadedConnectionPool:
        """Checks if there is a pool, then returns it else creates a new pool"""
        with self._pool_lock:
            pool = self._pool
            if not pool:
                pool = ThreadedConnectionPool(
                    self.min_pg_conns, self.max_pg_conns, **self.conn_args
                )
                self._pool = pool

        return pool

    def put_conn(self, conn: connection) -> None:
        """Returns connection to the pool"""
        self.get_pool().putconn(conn)

    def get_conn(self) -> connection:
        for _ in range(MAX_PG_CONNECT_RETRIES):
            conn = self.get_pool().getconn()

            if self._conn_is_closed(conn):
                self.close_all_conns()
                continue

            return conn
        raise OperationalError("No open connection available")

    @staticmethod
    def _conn_is_closed(conn: connection) -> bool:
        """Verify that a connection is still open"""
        if conn.closed != 0:
            return True

        try:
            with conn.cursor() as curs:
                curs.execute("SELECT 1;")
            conn.commit()
            return False

        except OperationalError:
            return True

    @staticmethod
    def _get_env_args() -> dict:
        return {
            "dbname": os.environ.get("POSTGRES_DB_NAME"),
            "user": os.environ.get("POSTGRES_USER"),
            "password": os.environ.get("POSTGRES_PASSWORD"),
            "host": os.environ.get("POSTGRES_HOST"),
            "port": os.environ.get("POSTGRES_PORT"),
            "connect_timeout": os.environ.get("POSTGRES_CONNECT_TIMEOUT"),
            "application_name": "take_home_test",
        }

    @staticmethod
    def _get_args(**kwargs) -> dict:
        """Get connection args"""
        args = Pool._get_env_args()
        args.update(kwargs)
        return args


class ConnectionPooler:
    """Singleton that holds connection pools to multiple DBs"""

    _pools: Dict[str, Pool] = {}
    _pool_lock = threading.Lock()

    @classmethod
    def get_pool(cls, pool_name: str = "default") -> Pool:
        """Get a connection pool by name"""
        with cls._pool_lock:
            return cls._pools[pool_name]

    @classmethod
    def register(cls, pool_name: str = "default", **conn_args) -> None:
        """Creates a pool with the given name"""

        with cls._pool_lock:
            cls._pools[pool_name] = Pool(**conn_args)

    @staticmethod
    @atexit.register
    def _close_all_pools() -> None:
        """Close all pools"""
        with ConnectionPooler._pool_lock:
            for pool in ConnectionPooler._pools:
                ConnectionPooler._pools[pool].close_all_conns()


ConnectionPooler.register("default")
