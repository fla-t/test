# mypy: ignore-errors
# type: ignore
from datetime import date, datetime, timezone
from itertools import combinations
from typing import List
from uuid import uuid4

import pytest
from services.sales.domain.models import Sale
from services.sales.entrypoint import unit_of_work as uow


@pytest.mark.usefixtures("drop_sales_fk")
class TestSalesRepo:
    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_add(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sales = [Sale.create(str(uuid4()), 1)]

            uow.sales.add(sales)
            res = uow.sales.get([sales[0].id])

            assert res == sales

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_add(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sales: List[Sale] = [
                Sale(
                    id=str(uuid4()),
                    inventory_log_id=str(uuid4()),
                    price=100,
                    created_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
                Sale(
                    id=str(uuid4()),
                    inventory_log_id=str(uuid4()),
                    price=100,
                    created_at=datetime(2022, 1, 2, tzinfo=timezone.utc),
                ),
            ]

            uow.sales.add(sales)

        with selected_uow as uow:
            for sale in sales:
                assert uow.sales.get([sale.id]) == [sale]

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get_by_date_range(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sales: List[Sale] = [
                Sale(
                    id=str(uuid4()),
                    inventory_log_id=str(uuid4()),
                    price=100,
                    created_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
                ),
                Sale(
                    id=str(uuid4()),
                    inventory_log_id=str(uuid4()),
                    price=100,
                    created_at=datetime(2021, 1, 2, tzinfo=timezone.utc),
                ),
                Sale(
                    id=str(uuid4()),
                    inventory_log_id=str(uuid4()),
                    price=100,
                    created_at=datetime(2021, 1, 3, tzinfo=timezone.utc),
                ),
            ]

            uow.sales.add(sales)

        with selected_uow as uow:
            for start, end in combinations([1, 2, 3], r=2):
                res = uow.sales.get_sales_by_date_range(date(2021, 1, start), date(2021, 1, end))
                assert res == sales[start - 1 : end]
