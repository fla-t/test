import pytest
from services.inventory.entrypoint import unit_of_work as uow


@pytest.fixture(scope="class")
def db_uow(scratch_db) -> uow.DBPoolUnitOFWork:
    """Creates a DB unit of work with a scratch db setted up"""

    return uow.DBPoolUnitOFWork(scratch_db)


@pytest.fixture(scope="class")
def fake_uow() -> uow.FakeUnitOfWork:
    """Creates a Fake unit of work"""

    return uow.FakeUnitOfWork()


@pytest.fixture(scope="function")
def selected_uow(
    request, db_uow: uow.DBPoolUnitOFWork, fake_uow: uow.FakeUnitOfWork
) -> uow.AbstractUnitOfWork:
    """
    This is so we can test both fake and db repo at the same time,
    so we know for sure that they are perfectly consistent
    """

    if request.param == "db_uow":
        return db_uow
    elif request.param == "fake_uow":
        return fake_uow
    else:
        raise Exception(f"Error: What's that? {request.param}")
