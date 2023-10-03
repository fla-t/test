from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from services.sales.domain import models as mdl
from services.sales.entrypoint import commands as cmd
from services.sales.entrypoint.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_register_sale(selected_uow: AbstractUnitOfWork, drop_sales_fk, mocker):
    inventory_log_id = str(uuid4())

    mocker.patch(
        "services.sales.domain.models.now_in_utc",
        return_value=datetime(2021, 1, 1, tzinfo=timezone.utc),
    )

    sale_id = cmd.register_sale(selected_uow, inventory_log_id, 1)

    with selected_uow as uow:
        sale = uow.sales.get([sale_id])
        assert sale == [
            mdl.Sale(
                sale_id,
                inventory_log_id,
                1,
                datetime(2021, 1, 1, tzinfo=timezone.utc),
            )
        ]
