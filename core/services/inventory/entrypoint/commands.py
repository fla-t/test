from services.inventory.domain.models import InventoryLog
from services.inventory.entrypoint.unit_of_work import AbstractUnitOfWork


def create_inventory_log(uow: AbstractUnitOfWork, sku_id: str, quantity_changed: int) -> str:
    with uow:
        inventory_log = InventoryLog.create(sku_id, quantity_changed=quantity_changed)
        uow.inventory_logs.add([inventory_log])

    return inventory_log.id
