import pytest_asyncio
import pytest
from sqlalchemy import Table, Column, Integer, String, MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.uow.db import SQLAlchemyUnitOfWork

# Define a simple test table
metadata = MetaData()
test_table = Table(
    "test_table",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), nullable=False),
)


@pytest_asyncio.fixture(scope="module")
async def engine():
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    # Create the test table
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    # expire_on_commit=False so objects remain after commit
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.mark.asyncio
async def test_commit_in_uow(session_factory):
    uow = SQLAlchemyUnitOfWork(session_factory=session_factory)
    # Insert a row within the UoW
    async with uow:
        await uow.session.execute(test_table.insert().values(name="alice"))
    # After context, the row should be committed
    # Use a new session to verify
    async with session_factory() as session:
        result = await session.execute(select(test_table))
        rows = result.all()
    assert len(rows) == 1
    assert rows[0][1] == "alice"


@pytest.mark.asyncio
async def test_rollback_on_exception(session_factory):
    uow = SQLAlchemyUnitOfWork(session_factory=session_factory)

    class CustomError(Exception):
        pass

    # Attempt to insert and then raise
    with pytest.raises(CustomError):
        async with uow:
            await uow.session.execute(test_table.insert().values(name="bob"))
            raise CustomError()
    # After exception, the insertion should be rolled back
    async with session_factory() as session:
        result = await session.execute(select(test_table))
        rows = result.all()
    # Should still only have the previous 'alice' row
    assert all(row[1] != "bob" for row in rows)
