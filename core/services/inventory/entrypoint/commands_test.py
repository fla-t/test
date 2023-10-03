from uuid import uuid4

import pytest
from services.inventory.domain import models as mdl
from services.inventory.entrypoint import commands as cmd
from services.inventory.entrypoint.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_create_inventory_log(selected_uow: AbstractUnitOfWork, drop_inventory_fk):
    sku_id = str(uuid4())
    inventory_log_id = cmd.create_inventory_log(selected_uow, sku_id, 1)

    with selected_uow as uow:
        inventory_log = uow.inventory_logs.get([inventory_log_id])

    assert inventory_log == [mdl.InventoryLog(inventory_log_id, sku_id, 1)]
