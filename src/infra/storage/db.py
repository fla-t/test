from functools import lru_cache

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.infra.config import config

Base = declarative_base()


def db_url(sync: bool = False) -> str:
    engine = f"{config.db.engine}+asyncpg://" if not sync else f"{config.db.engine}://"

    url = (
        f"{engine}"
        f"{config.db.username}:{config.db.password}"
        f"@{config.db.host}:{config.db.port}"
        f"/{config.db.database_name}"
    )
    return url


def get_engine():
    """Returns a SQLAlchemy engine based on the configuration"""
    return create_async_engine(db_url(), pool_size=10, max_overflow=20, pool_timeout=120)


def get_session_factory():
    """Returns a SQLAlchemy session factory based on the configuration"""
    return async_sessionmaker(bind=get_engine(), expire_on_commit=True, autoflush=False)
