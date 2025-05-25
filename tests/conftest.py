import uuid
from urllib.parse import urlparse
from typing import AsyncGenerator

import asyncpg
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command

from src.infra.config import config


def _parse_db_url(db_url: str) -> dict[str, str | int | None]:
    """
    Parses a SQLAlchemy-style URL into components for asyncpg.
    """
    normalized = db_url.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urlparse(normalized)
    return {
        "host": parsed.hostname,
        "port": parsed.port,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/"),
    }


@pytest_asyncio.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    """
    Fixture to set up a PostgreSQL container asynchronously.
    """
    container = PostgresContainer(
        "postgres:latest", username=config.db.username, password=config.db.password
    )
    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture(scope="session")
async def template_database_creation(postgres_container: PostgresContainer) -> str:
    """
    Async fixture to create a template database for tests.
    """
    pg_url = postgres_container.get_connection_url()
    admin_config = _parse_db_url(pg_url)
    admin_config["database"] = "postgres"

    admin_connection: asyncpg.Connection = await asyncpg.connect(**admin_config)
    try:
        await admin_connection.execute("DROP DATABASE IF EXISTS template_test_db;")
        await admin_connection.execute("CREATE DATABASE template_test_db;")
    finally:
        await admin_connection.close()

    target_db_url = pg_url.rsplit("/", 1)[0] + "/template_test_db"
    cfg = Config()
    cfg.set_main_option("script_location", "src/infra/storage/migrations")
    cfg.set_main_option("sqlalchemy.url", target_db_url)
    command.upgrade(cfg, "head")

    return target_db_url


@pytest_asyncio.fixture(scope="function")
async def database_creation(
    postgres_container: PostgresContainer, template_database_creation: str
) -> AsyncGenerator[str, None]:
    """
    Async fixture to spin up a fresh test DB per function.
    """
    pg_url = postgres_container.get_connection_url()
    admin_conf = _parse_db_url(pg_url)
    admin_conf["database"] = "postgres"

    db_name = f"test_db_{uuid.uuid4().hex}"

    admin_connection: asyncpg.Connection = await asyncpg.connect(**admin_conf)
    try:
        await admin_connection.execute(f"CREATE DATABASE {db_name} TEMPLATE template_test_db;")
    finally:
        await admin_connection.close()

    config.db.host = postgres_container.get_container_host_ip()
    config.db.port = int(postgres_container.get_exposed_port(5432))
    config.db.username = postgres_container.username
    config.db.password = postgres_container.password
    config.db.database_name = db_name

    test_db_url = pg_url.rsplit("/", 1)[0] + f"/{db_name}"

    try:
        yield test_db_url
    finally:
        admin_connection = await asyncpg.connect(**admin_conf)
        try:
            await admin_connection.execute(
                """
                    select pg_terminate_backend(pid)
                    from pg_stat_activity
                    where datname = $1
                        and pid <> pg_backend_pid()
                    ;
                """,
                db_name,
            )
            await admin_connection.execute(f"DROP DATABASE IF EXISTS {db_name};")
        finally:
            await admin_connection.close()
