from uuid import uuid4

from services.inventory.domain.models import SKU, InventoryLog
from services.inventory.entrypoint import queries as qry
from services.inventory.entrypoint.unit_of_work import DBPoolUnitOFWork


def test_inventory_by_skus(db_uow: DBPoolUnitOFWork):
    # seed some skus
    skus = [SKU.create("sku1", "sku1 description"), SKU.create("sku2", "sku2 description")]
    inventory_logs = [
        InventoryLog.create(sku_id=skus[0].id, quantity_changed=10),
        InventoryLog.create(sku_id=skus[0].id, quantity_changed=10),
        InventoryLog.create(sku_id=skus[0].id, quantity_changed=10),
        InventoryLog.create(sku_id=skus[1].id, quantity_changed=20),
        InventoryLog.create(sku_id=skus[1].id, quantity_changed=-20),
        InventoryLog.create(sku_id=skus[0].id, quantity_changed=-10),
    ]

    with db_uow as uow:
        uow.skus.save(skus)
        uow.inventory_logs.add(inventory_logs)

    # test

    res = qry.inventory_by_skus(db_uow, [skus[0].id, skus[1].id])

    res_dict = {r.sku_id: r.quantity for r in res}

    assert res_dict[skus[0].id] == 20
    assert res_dict[skus[1].id] == 0
