import pytest
from services.inventory.entrypoint import unit_of_work as uow


@pytest.fixture(scope="class")
def db_uow(scratch_db) -> uow.DBPoolUnitOfWork:
    """Creates a DB unit of work with a scratch db setted up"""

    return uow.DBPoolUnitOfWork()


@pytest.fixture(scope="class")
def fake_uow() -> uow.FakeUnitOfWork:
    """Creates a Fake unit of work"""

    return uow.FakeUnitOfWork()


@pytest.fixture(scope="function")
def selected_uow(
    request, db_uow: uow.DBPoolUnitOfWork, fake_uow: uow.FakeUnitOfWork
) -> uow.AbstractUnitOfWork:
    """
    This is so we can test both fake and db repo at the same time,
    so we know for sure that they are perfectly consistent
    """

    match request.param:
        case "db_uow":
            return db_uow
        case "fake_uow":
            return fake_uow
        case _:
            raise Exception(f"Error: What's that? {request.param}")


@pytest.fixture(scope="class")
def drop_inventory_fk(db_uow: uow.DBPoolUnitOfWork):
    sql = """
        alter table inventory_logs drop constraint inventory_logs_sku_id_fkey;
    """

    with db_uow, db_uow.db_pool.cursor() as curs:
        curs.execute(sql)
