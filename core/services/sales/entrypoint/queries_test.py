from datetime import date, datetime, timezone
from uuid import uuid4

from services.sales.domain.models import Sale
from services.sales.entrypoint import commands as cmd
from services.sales.entrypoint import queries as qry
from services.sales.entrypoint import unit_of_work as uow


def test_sales_by_time_period_by_day(db_uow: uow.DBPoolUnitOfWork, drop_sales_fk):
    # seed a lot of data
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
    ]

    with db_uow as uow:
        uow.sales.add(sales)

    # test

    res = qry.sales_by_time_period(
        db_uow, start=date(2021, 1, 2), end=date(2021, 1, 3), time_period="day"
    )

    assert len(res) == 2
    assert res[0].revenue == 80
    assert res[1].revenue == 42
