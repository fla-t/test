from uuid import uuid4

import pytest
from services.catalog.domain import models as mdl
from services.catalog.entrypoint import commands as cmd
from services.catalog.entrypoint.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_create_sku(selected_uow: AbstractUnitOfWork, drop_skus_fk):
    category_id = str(uuid4())
    sku_id = cmd.create_sku(selected_uow, category_id, "name", "description")

    with selected_uow as uow:
        assert uow.skus.get([sku_id]) == [mdl.Sku(sku_id, category_id, "name", "description")]


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_update_sku(selected_uow: AbstractUnitOfWork, drop_skus_fk):
    sku_id = cmd.create_sku(
        selected_uow, name="name", category_id=str(uuid4()), description="description"
    )

    with selected_uow as uow:
        sku = uow.skus.get([sku_id])
        assert sku == [mdl.Sku(sku_id, "name", "description")]

    new_cat_id = str(uuid4())
    sku_id = cmd.update_sku(selected_uow, sku_id, new_cat_id, "new_name", "new_description")

    with selected_uow as uow:
        assert uow.skus.get([sku_id]) == [
            mdl.Sku(sku_id, new_cat_id, "new_name", "new description")
        ]


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_create_category(selected_uow: AbstractUnitOfWork):
    category_id = cmd.create_category(selected_uow, "fresh")

    with selected_uow as uow:
        assert uow.categories.get([category_id]) == [mdl.Category(category_id, "fresh")]


@pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
def test_update_sku(selected_uow: AbstractUnitOfWork):
    category_id = cmd.create_category(selected_uow, "fresh")

    with selected_uow as uow:
        assert uow.categories.get([category_id]) == [mdl.Category(category_id, "fresh")]

    cmd.update_category(selected_uow, category_id, "frozen")

    with selected_uow as uow:
        assert uow.categories.get([category_id]) == [mdl.Category(category_id, "frozen")]
