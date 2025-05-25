import asyncio
from contextlib import asynccontextmanager

from src.infra.storage.db import db_url
from fastapi import FastAPI
from alembic import command
from alembic.config import Config


@asynccontextmanager
async def lifespan_builder(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    This is used to manage resources that need to be initialized and cleaned up
    when the application starts and stops.
    """

    # run any new migrations (if exist)
    def run_migrations():
        cfg = Config()
        cfg.set_main_option("script_location", "src/infra/storage/migrations")
        cfg.set_main_option("sqlalchemy.url", db_url())
        command.upgrade(cfg, "head")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_migrations)

    yield
