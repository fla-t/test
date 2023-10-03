import pytest
from services.catalog.domain import models as mdl
from services.catalog.entrypoint import commands as cmd
from services.catalog.entrypoint.unit_of_work import AbstractUnitOfWork


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
