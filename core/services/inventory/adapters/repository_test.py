# mypy: ignore-errors
# type: ignore
from uuid import uuid4

import pytest
from services.inventory.domain.models import InventoryLog
from services.inventory.entrypoint import unit_of_work as uow


@pytest.mark.usefixtures("drop_inventory_fk")
class TestInventoryLogsRepo:
    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            inventory_log = InventoryLog.create(str(uuid4()), quantity_changed=1)
            uow.inventory_logs.add([inventory_log])
            assert uow.inventory_logs.get([inventory_log.id]) == [inventory_log]

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_add(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            # seed an inventory log
            il1 = InventoryLog.create(str(uuid4()), quantity_changed=1)
            il2 = InventoryLog.create(str(uuid4()), quantity_changed=100)
            uow.inventory_logs.add([il1, il2])

            assert uow.inventory_logs.get([il1.id, il2.id]) == [il1, il2]
