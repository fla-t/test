from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.infra.config import config

Base = declarative_base()


def db_url(sync: bool = False) -> str:

    url = (
        f"{config.db.engine}+asyncpg://"
        if not sync
        else f"{config.db.engine}://"
        f"{config.db.username}:{config.db.password}"
        f"@{config.db.host}:{config.db.port}"
        f"/{config.db.database_name}"
    )
    return url


# One engine and one sessionmaker for the whole application
engine = create_async_engine(db_url(), pool_size=10, max_overflow=20, pool_timeout=120)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=True, autoflush=False)
