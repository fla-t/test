from uuid import uuid4

from services.inventory.domain.models import InventoryLog
from services.inventory.entrypoint import queries as qry
from services.inventory.entrypoint.unit_of_work import DBPoolUnitOfWork


def test_inventory_by_skus(db_uow: DBPoolUnitOfWork, drop_inventory_fk):
    # seed some skus
    sku_ids = [str(uuid4()) for _ in range(2)]
    inventory_logs = [
        InventoryLog.create(sku_id=sku_ids[0], quantity_changed=10),
        InventoryLog.create(sku_id=sku_ids[0], quantity_changed=10),
        InventoryLog.create(sku_id=sku_ids[0], quantity_changed=10),
        InventoryLog.create(sku_id=sku_ids[1], quantity_changed=20),
        InventoryLog.create(sku_id=sku_ids[1], quantity_changed=-20),
        InventoryLog.create(sku_id=sku_ids[0], quantity_changed=-10),
    ]

    with db_uow as uow:
        uow.inventory_logs.add(inventory_logs)

    # test

    res = qry.inventory_by_skus(db_uow, [sku_ids[0], sku_ids[1]])

    res_dict = {r.sku_id: r.quantity for r in res}

    assert res_dict[sku_ids[0]] == 20
    assert res_dict[sku_ids[1]] == 0
