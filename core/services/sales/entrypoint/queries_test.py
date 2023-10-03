from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from services.sales.domain.models import Sale
from services.sales.entrypoint import commands as cmd
from services.sales.entrypoint import queries as qry
from services.sales.entrypoint import unit_of_work as uow


@pytest.fixture(scope="class")
def setup_for_sales_by_time_period(db_uow: uow.DBPoolUnitOfWork):
    sales = [
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=10,
            created_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
        ),
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=20,
            created_at=datetime(2021, 1, 2, tzinfo=timezone.utc),
        ),
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=60,
            created_at=datetime(2021, 1, 2, tzinfo=timezone.utc),
        ),
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=42,
            created_at=datetime(2021, 1, 3, tzinfo=timezone.utc),
        ),
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=100,
            created_at=datetime(2021, 1, 4, tzinfo=timezone.utc),
        ),
        Sale(
            id=str(uuid4()),
            inventory_log_id=str(uuid4()),
            price=100,
            created_at=datetime(2021, 2, 1, tzinfo=timezone.utc),
        ),
    ]

    with db_uow as uow:
        uow.sales.add(sales)


def test_sales_by_time_period_by_day(
    db_uow: uow.DBPoolUnitOfWork, drop_sales_fk, setup_for_sales_by_time_period
):
    res = qry.sales_by_time_period(
        db_uow, time_period="day", start=date(2021, 1, 2), end=date(2021, 1, 3)
    )
    assert len(res) == 2
    assert res[0].sales == 80
    assert res[1].sales == 42

    res = qry.sales_by_time_period(db_uow, start=date(2020, 12, 28), time_period="week")
    assert len(res) == 1
    assert res[0].period == date(2020, 12, 28)  # thats where the week 2021, 01, 01 started
    assert res[0].sales == 132

    res = qry.sales_by_time_period(db_uow, start=date(2021, 1, 1), time_period="month")
    assert len(res) == 1
    assert res[0].period == date(2021, 1, 1)  # thats where the month started
    assert res[0].sales == 232

    res = qry.sales_by_time_period(db_uow, start=date(2021, 1, 1), time_period="year")
    assert len(res) == 1
    assert res[0].period == date(2021, 1, 1)  # thats where the year started
    assert res[0].sales == 332
