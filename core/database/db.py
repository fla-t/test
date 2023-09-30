import os
from typing import Optional

from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extensions import cursor as pg_cursor
from psycopg2.extras import DictCursor

SERIALIZATION_ERROR_SLEEP_BASE_TIME = 0.2  # Seconds
SERIALIZATION_ERROR_RETRIES = 4


class BaseDatabase:
    """Base database class"""

    def __init__(self) -> None:
        # this will be set by the subclasses
        self._conn: connection

    def __enter__(self) -> "BaseDatabase":
        return self

    def __exit__(self, type, value, traceback) -> None:
        try:
            if type or value or traceback:
                self._conn.rollback()
            else:
                self._conn.commit()
        finally:
            self._conn.close()

    def conn(self) -> Optional[connection]:
        return self._conn

    def cursor(self, *args, **kwargs) -> pg_cursor:
        return self._conn.cursor(*args, **kwargs)

    def dict_cursor(self) -> pg_cursor:
        return self._conn.cursor(cursor_factory=DictCursor)

    def args() -> dict:
        return {
            "dbname": os.environ.get("POSTGRES_DB"),
            "user": os.environ.get("POSTGRES_USER"),
            "password": os.environ.get("POSTGRES_PASSWORD"),
            "host": os.environ.get("POSTGRES_HOST"),
            "port": os.environ.get("POSTGRES_PORT"),
            "connect_timeout": os.environ.get("POSTGRES_CONNECT_TIMEOUT"),
            "application_name": "take_home_test",
        }


class Database(BaseDatabase):
    def __init__(self) -> None:
        """Establishes DB connection, by default, pulls conn details from environment variables"""

        super().__init__()
        self._conn = connect(**self.args())
