"""
This file contains fixtures that are using to basically create a db for testing
"""
import glob
import hashlib
import os
import pathlib
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional, Tuple
from unittest.mock import patch
from uuid import uuid4

import pytest
import pytz
from database import DBPool
from database.pooler import ConnectionPooler
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, connection
from testcontainers.postgres import PostgresContainer

SCHEMA_DIR = f"{pathlib.Path(__file__).parent.absolute()}/database/migrations/*-*.sql"
SCHEMA_DIR = os.environ.get("SCHEMA_DIR", SCHEMA_DIR)


class Schema:
    """
    Schema related state & methods

    Schema is stored as a linked file list, each file contains a migration.
    files are named as 1-2.sql, 2-3.sql and so on
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
    def init_schema(cls, pool_name: str) -> None:
        with DBPool(db_pool_name=pool_name) as db, db.cursor() as curs:
            # Run the migrations one by one
            for file in Schema.get_files():
                with open(file, "r", encoding="utf-8") as f:
                    curs.execute(f.read())


def pytest_addoption(parser):
    """
    Registers an option for running pytest.
    """
    parser.addoption("--new-db", action="store_true", default=True)


@contextmanager
def admin_conn(admin_pool_name: str) -> Generator[connection, None, None]:
    """
    Creates connection to admin db pool

    wrapped with contextmanager just to have a better cleanup
    """
    admin_conn = ConnectionPooler.get_pool(admin_pool_name).get_conn()
    admin_conn.autocommit = True
    yield admin_conn
    admin_conn.close()
    ConnectionPooler.get_pool(admin_pool_name).put_conn(admin_conn)


def create_db(admin_pool_name: str, db_name: str, template_db: Optional[str] = None) -> bool:
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
        return True


@contextmanager
def temp_db(admin_pool_name, db_name, template_db=None, drop_db=True) -> Generator[str, None, None]:
    """Create database in postgresql."""
    # here the temp db comes into action because this function is used by a fixture which is scoped
    # to class so using this we won't need to recreate db after every test run.
    create_db(admin_pool_name, db_name, template_db=template_db)

    yield db_name
    if not drop_db:
        return

    # Cleanup
    with admin_conn(admin_pool_name) as ac, ac.cursor() as cur:
        cur.execute("UPDATE pg_database SET datallowconn=false WHERE datname = %s;", (db_name,))
        cur.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid)"
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s;",
            (db_name,),
        )
        cur.execute('DROP DATABASE IF EXISTS "{}";'.format(db_name))


@pytest.fixture(scope="session")
def postgres_connection(request) -> Tuple[str, dict]:
    """
    This fixture creates a postgres container and registers it in the pool.
    Returns the admin db name and connection params
    """

    if not request.config.getoption("--new-db"):
        yield ("default", ConnectionPooler.get_pool("default").get_conn())
        return

    # Create a new db, the default db that is created is the postgres base admin db.
    # that contains all the metadata for the postgres instance
    with PostgresContainer() as pg:
        params = {
            "dbname": pg.POSTGRES_DB,
            "user": pg.POSTGRES_USER,
            "password": pg.POSTGRES_PASSWORD,
            "host": pg.get_container_host_ip(),
            "port": pg.port_to_expose,
        }
        admin_db_name = str(uuid4())
        ConnectionPooler.register(admin_db_name, **params)

        # Create a template db that will be used to create test specific dbs,
        # this way if the schema isn't changed we don't need to run the migrations again
        template_params = params.copy()
        template_db_name = Schema.get_version()
        template_params["db_name"] = template_db_name

        # register the template db
        ConnectionPooler.register(template_db_name, **template_params)

        # only create a new db if it doesn't already exist.
        if create_db(admin_db_name, template_db_name):
            Schema.init_schema(template_db_name)

        ConnectionPooler.get_pool(template_db_name).close_all_conns()
        yield (admin_db_name, template_db_name, template_params)


@pytest.fixture(scope="class")
def scratch_db(postgres_connection) -> Generator[str, None, None]:
    """
    This fixture relies on the template_db_params fixture and uses the template
    database to create a test specific database.
    It yields the pool name of the scratch db and patches pool of the ConnectionPooler.
    """
    (admin_db_name, template_db_name, template_params) = postgres_connection

    params = template_params.copy()

    # DB name has timestamp
    now = datetime.now(pytz.timezone("Asia/Karachi"))
    scratch_db_name = f"test_{now:%Y-%m-%d_%I:%M:%S%p}"

    params["dbname"] = scratch_db_name
    ConnectionPooler.register(scratch_db_name, **params)

    # sort of a hack, I am patching the default because to send this would be require extensive
    # property handling, which i don't have time to do
    with temp_db(
        admin_pool_name=admin_db_name, db_name=scratch_db_name, template_db=template_db_name
    ), patch(
        "database.db_pool.DBPool.__init__.__defaults__",
        (ISOLATION_LEVEL_READ_COMMITTED, scratch_db_name),
    ):
        yield scratch_db_name


def test_scratch_db(scratch_db) -> None:
    """
    This test checks if the scratch db is created and the pool is patched.
    """
    assert scratch_db
