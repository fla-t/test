from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infra.config import config


def _db_url() -> str:
    url = f"{config.db.engine}+asyncpg://"

    if config.db.username:
        url += f"{config.db.username}"
        if config.db.password:
            url += f":{config.db.password}"
        url += "@"

    url += f"{config.db.host}"

    if config.db.port:
        url += f":{config.db.port}"

    url += f"/{config.db.database_name}"
    return url


# One engine and one sessionmaker for the whole application
engine = create_async_engine(_db_url(), pool_size=10, max_overflow=20, pool_timeout=120)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=True, autoflush=False)
