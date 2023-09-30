import glob
import hashlib
import os
import pathlib
from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple
from uuid import uuid4

import pytest
from database.db_pool import DBPool
from database.pooler import ConnectionPooler
from psycopg2.extensions import connection, cursor
from testcontainers.postgres import PostgresContainer

SCHEMA_DIR = f"{pathlib.Path(__file__).parent.absolute()}/database/migrations/*-*.sql"
SCHEMA_DIR = os.environ.get("SCHEMA_DIR", SCHEMA_DIR)


class Schema:
    """
    Schema related state & methods
    """

    _schema_filenames: List[str] = []
    _schema_version: str = ""

    @classmethod
    def get_files(cls) -> List[str]:
        """Gets the schema files"""

        if not cls._schema_filenames:
            schema_files = glob.glob(SCHEMA_DIR)

            # sort the files, schema files are inserted as 1-2.sql, 2-3.sql and so on
            schema_files.sort(key=lambda x: x.split("/")[-1].split("-")[0])
            cls._schema_filenames = schema_files

        return cls._schema_filenames

    @classmethod
    def get_version(cls) -> str:
        """Gets the schema version"""

        if not cls._schema_version:
            m = hashlib.sha256()
            for fn in cls.get_files():
                with open(fn, "r", encoding="utf-8") as f:
                    m.update(f.read().encode("utf-8"))

            cls._schema_version = m.hexdigest()

        return cls._schema_version

    @classmethod
    def init_schema(pool_name: str) -> None:
        with DBPool(db_pool_name=pool_name) as db, db.cursor() as curs:
            # Run the migrations one by one
            for file in Schema.get_files():
                with open(file, "r", encoding="utf-8") as f:
                    curs.execute(f.read())


@pytest.fixture(scope="session")
def postgres_connection(request) -> Tuple[str, dict]:
    """
    This fixture creates a postgres container and registers it in the pool.
    Returns the admin db name and connection params
    """

    if not request.config.getoption("--new-db"):
        yield ("default", ConnectionPooler.get_pool("default").get_conn())
        return

    with PostgresContainer() as pg:
        params = {
            "dbname": pg.POSTGRES_DB,
            "user": pg.POSTGRES_USER,
            "password": pg.POSTGRES_PASSWORD,
            "host": pg.get_container_host_ip(),
            "port": pg.port_to_expose,
        }
        db_name = str(uuid4())
        ConnectionPooler.register(db_name, **params)
        yield (db_name, params)


@contextmanager
def admin_conn(admin_pool_name: str) -> Generator[connection]:
    """
    Creates connection to admin db pool

    :param admin_pool_name: Name of admin pool
    """
    admin_conn = ConnectionPooler.get_pool(admin_pool_name).get_conn()
    admin_conn.autocommit = True
    yield admin_conn
    admin_conn.close()
    ConnectionPooler.get_pool(admin_pool_name).put_conn(admin_conn)


def create_db(admin_pool_name: str, db_name: str, template_db: Optional[str] = None):
    """
    Creates a db if it doesn't already exist.
    Returns True if a db was created, False if it already exists.
    """

    with admin_conn(admin_pool_name) as ac, ac.cursor() as cur:
        cur.execute("SELECT datname FROM pg_catalog.pg_database WHERE datname = %s;", (db_name,))
        if cur.fetchone():
            return False
        if not template_db:
            cur.execute(f'CREATE DATABASE "{db_name}";')
        else:
            cur.execute(f'CREATE DATABASE "{db_name}" TEMPLATE "{template_db}";')
        return True


@pytest.fixture(scope="session")
def template_db(postgres_connection) -> Generator[str, str, str]:
    (admin_db_name, admin_params) = postgres_connection

    template_params = admin_params.copy()
    template_db_name = Schema.get_version()
    template_params["db_name"] = template_db_name
    ConnectionPooler.register(template_db_name, **template_params)

    if create_db(admin_db_name, template_db_name):
        Schema.init_schema(template_db_name)

    ConnectionPooler.get_pool(template_db_name).close_all_conns()
    yield (admin_db_name, template_db_name, template_params)
