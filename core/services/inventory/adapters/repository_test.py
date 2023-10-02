# mypy: ignore-errors
# type: ignore
from uuid import uuid4

import pytest
from services.inventory.domain.models import SKU, InventoryLog
from services.inventory.entrypoint import unit_of_work as uow


class TestSKURepo:
    def setup_method(self):
        self.args = {
            "id": str(uuid4()),
            "name": "test_name",
            "description": "test_description",
        }

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            skus = [SKU(**self.args)]

            uow.skus.save([SKU(**self.args)])
            res = uow.skus.get([self.args["id"]])

            assert res == skus

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_save(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sku = SKU(**self.args)

            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]

        # small change
        sku.name = "Someother name"

        with selected_uow as uow:
            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]


class TestInventoryLogsRepo:
    def setup_method(self):
        self.sku_args = {
            "id": str(uuid4()),
            "name": "test_name",
            "description": "test_description",
        }

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            # seed an sku
            sku = SKU(**self.sku_args)
            uow.skus.save([sku])

            # seed an inventory log
            inventory_log = InventoryLog.create(sku.id, quantity_changed=1)
            uow.inventory_logs.add([inventory_log])
            assert uow.inventory_logs.get([inventory_log.id]) == [inventory_log]

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_add(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            # seed an sku
            sku = SKU(**self.sku_args)
            uow.skus.save([sku])

            # seed an inventory log
            il1 = InventoryLog.create(sku.id, quantity_changed=1)
            il2 = InventoryLog.create(sku.id, quantity_changed=100)
            uow.inventory_logs.add([il1, il2])

            assert uow.inventory_logs.get([il1.id, il2.id]) == [il1, il2]
