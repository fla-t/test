from uuid import uuid4

import pytest
from services.inventory.domain import models as mdl
from services.inventory.entrypoint import commands as cmd
from services.inventory.entrypoint.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_create_inventory_log(selected_uow: AbstractUnitOfWork):
    with selected_uow as uow:
        sku = mdl.SKU.create("name", "description")
        uow.skus.save([sku])

    inventory_log_id = cmd.create_inventory_log(selected_uow, sku.id, 1)

    with selected_uow as uow:
        inventory_log = uow.inventory_logs.get([inventory_log_id])

    assert inventory_log == [mdl.InventoryLog(inventory_log_id, sku.id, 1)]


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_create_sku(selected_uow: AbstractUnitOfWork):
    sku_id = cmd.create_sku(selected_uow, "name", "description")

    with selected_uow as uow:
        assert uow.skus.get([sku_id]) == [mdl.SKU(sku_id, "name", "description")]


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_update_sku(selected_uow: AbstractUnitOfWork):
    sku_id = cmd.create_sku(selected_uow, "name", "description")

    with selected_uow as uow:
        sku = uow.skus.get([sku_id])
        assert sku == [mdl.SKU(sku_id, "name", "description")]

    sku[0].name = "new_name"
    sku_id = cmd.update_sku(selected_uow, sku_id, "new_name", "description")

    with selected_uow as uow:
        assert uow.skus.get([sku_id]) == sku
